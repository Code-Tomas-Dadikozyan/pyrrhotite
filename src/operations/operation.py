"""
Symmetry operation: matrix construction, application to atoms, equality check.
Translated from the original C++ `schoenflies` (was reference/src/symmetry/
operations/operation.h/cpp; that vendored tree was removed in 0.2.0 — see
https://gitlab.com/lkkmpn/schoenflies).

What is a symmetry operation?
------------------------------
A symmetry operation is a transformation of 3-D space that leaves a molecule
looking identical to how it started.  Every such operation can be represented
as a 3×3 matrix R acting on the column vector of atom coordinates.

The four types used in Schoenflies notation:

  Cn  — proper rotation by 360°/n about an axis.
        C2 is a half-turn; C6 is a 60° rotation (as in benzene).
  Sn  — improper rotation: a Cn rotation followed immediately by reflection
        through the plane perpendicular to the axis.  S1 = σ, S2 = i.
  σ   — reflection through a plane passing through the origin.
  i   — inversion through the origin (x,y,z → -x,-y,-z).

Finding which of these operations exist for a given molecule is the central
task of the symmetry algorithm; the set of operations that exist forms the
point group.
"""

from __future__ import annotations

import copy
import math
from typing import TYPE_CHECKING

import numpy as np

from .operation_label import OperationLabel

if TYPE_CHECKING:
    from ..structure import Structure


class Operation:
    """A single symmetry operation with its transformation matrix and atom-mapping data."""

    # Sentinel value used for infinite-order axes (C∞ in linear molecules).
    # Using 0 avoids allocating a special float; all code that builds rotation
    # angles checks `if self.degree == DEGREE_INF` before dividing by degree.
    DEGREE_INF: int = 0  # sentinel for infinite-order axes (C∞, S∞)

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        """Create an uninitialised operation (use factory classmethods instead)."""
        self.id: int = 0
        self.label: OperationLabel = OperationLabel(OperationLabel.Element.Inversion)
        self.degree: int = 0
        self.axis: np.ndarray = np.zeros(3, dtype=float)
        self.matrix: np.ndarray = np.eye(3, dtype=float)
        # _error is set by do_operation() to the worst-case mis-mapping distance.
        # It starts as NaN so that reading it before the operation is applied
        # raises a clear error rather than returning a misleading 0.
        self._error: float = float("nan")
        # result_indices_forwards[i] = j means: atom i maps to atom j under
        # one application of this operation.  result_indices_backwards is the
        # reverse map, needed for higher-order axes (e.g. C3 needs C3^-1 too).
        self.result_indices_forwards: list[int] = []
        self.result_indices_backwards: list[int] = []

    @classmethod
    def inversion(cls) -> Operation:
        """Construct an inversion operation (i)."""
        op = cls()
        op.label = OperationLabel(OperationLabel.Element.Inversion)
        op.matrix = op._calculate_matrix_inversion(1.0)
        return op

    @classmethod
    def reflection(cls, normal: np.ndarray) -> Operation:
        """Construct a reflection operation (σ) with the given plane normal."""
        op = cls()
        op.label = OperationLabel(OperationLabel.Element.Reflection)
        op.axis = normal / np.linalg.norm(normal)
        op.matrix = op._calculate_matrix_reflection(1.0)
        return op

    @classmethod
    def rotation(
        cls,
        element: OperationLabel.Element,
        degree: int,
        axis: np.ndarray,
    ) -> Operation:
        """Construct a proper or improper rotation (Cn / Sn) with the given axis."""
        if element not in (
            OperationLabel.Element.ProperRotation,
            OperationLabel.Element.ImproperRotation,
        ):
            raise ValueError("rotation() requires ProperRotation or ImproperRotation element.")
        op = cls()
        op.label = OperationLabel(element, degree=degree)
        op.degree = degree
        op.axis = axis / np.linalg.norm(axis)
        op.matrix = op._calculate_matrix(1.0)
        return op

    # ------------------------------------------------------------------
    # Setters (public attributes serve as getters directly)
    # ------------------------------------------------------------------

    def set_id(self, id: int) -> None:
        """Set the unique ID."""
        self.id = id

    def set_label(self, label: OperationLabel) -> None:
        """Replace the label."""
        self.label = label

    @property
    def error(self) -> float:
        """Return the operation error (must call do_operation first)."""
        if math.isnan(self._error):
            raise RuntimeError("Tried to get the error of a symmetry operation before it was computed.")
        return self._error

    def result_index(self, index: int) -> int:
        """Return the atom index that atom `index` maps to under this operation.

        For degree > 2, follows the chain abs(multiple) times using the
        forwards or backwards index map depending on the sign of multiple.
        """
        if self.label.multiple > 0:
            result_indices = self.result_indices_forwards
        else:
            result_indices = self.result_indices_backwards

        result_index = index
        for _ in range(abs(self.label.multiple)):
            result_index = result_indices[result_index]
        return result_index

    # ------------------------------------------------------------------
    # Equality
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Two operations are equal if they represent the same geometric element.

        For rotations and reflections, "same axis" is checked via the dot product:
        two unit vectors point along the same line if |u · v| ≈ 1 (they may
        point in opposite directions, which is the same axis).  The tolerance
        1 - |u·v| < 0.01 allows for ~8° angular error, which is generous but
        necessary to avoid counting near-duplicate axes found by the search.

        This equality is used by OperationManager to deduplicate the list of
        candidate operations discovered during the symmetry search.
        """
        if not isinstance(other, Operation):
            return NotImplemented
        if self.label.element != other.label.element:
            return False
        elem = self.label.element
        if elem == OperationLabel.Element.Inversion:
            # There is only one inversion centre (the origin), so two inversion
            # operations are always the same.
            return True
        if elem in (OperationLabel.Element.ProperRotation, OperationLabel.Element.ImproperRotation):
            return (
                self.degree == other.degree
                and 1 - abs(float(np.dot(self.axis, other.axis))) < 0.01
            )
        if elem == OperationLabel.Element.Reflection:
            # A mirror plane is fully determined by its normal vector; opposite
            # normals describe the same plane, so we use the absolute dot product.
            return 1 - abs(float(np.dot(self.axis, other.axis))) < 0.01
        raise RuntimeError("Unexpected symmetry element encountered.")

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    def do_operation(self, structure: Structure) -> None:
        """Apply this operation to all atoms in structure; set error and result_indices.

        The algorithm for testing whether an operation is a true symmetry:
        1. Transform each atom coordinate by the operation matrix.
        2. Find the nearest atom of the *same element* at the transformed position.
        3. Measure how far the transformed position is from that nearest atom.
        4. Record the worst-case distance as self.error.

        After this call, self.error is compared against a threshold in the
        symmetry search: if the error is small enough, the operation is a valid
        symmetry; otherwise it is discarded.

        The error is normalised by the atom's distance to the symmetry element
        (axis or plane) when that distance exceeds 1 Å.  This makes the
        criterion scale-invariant: atoms far from the axis are expected to move
        more in absolute terms, so the same angular error produces a larger raw
        distance — normalisation corrects for this.
        """
        max_error = 0.0
        n = structure.num_atoms
        self.result_indices_forwards = [0] * n
        # The backwards map is only needed for degree > 2 (e.g. C3 needs C3^-1
        # to follow chains of mappings in get_result_index).
        if self.label.degree > 2:
            self.result_indices_backwards = [0] * n

        for i in range(n):
            # Apply the 3×3 matrix to get the predicted new position.
            after = self.do_atom_operation(structure.coordinates[i])
            # Find the real atom of the same element closest to that prediction.
            closest = structure.find_closest_index(after, int(structure.atomic_numbers[i]))
            distance = float(np.linalg.norm(after - structure.coordinates[closest]))
            dist_to_elem = self._get_distance_to_element(after)
            # Normalise by distance to the symmetry element for atoms far from it.
            error = distance / dist_to_elem if dist_to_elem > 1.0 else distance
            if error > max_error:
                max_error = error
            self.result_indices_forwards[i] = closest
            if self.label.degree > 2:
                self.result_indices_backwards[closest] = i

        self._error = max_error

    def do_atom_operation(self, coordinates: np.ndarray) -> np.ndarray:
        """Apply the transformation matrix to a single atom coordinate vector."""
        return self.matrix @ coordinates

    def _get_distance_to_element(self, coordinates: np.ndarray) -> float:
        """Return the distance from coordinates to this operation's symmetry element."""
        elem = self.label.element
        if elem == OperationLabel.Element.Inversion:
            return float(np.linalg.norm(coordinates))
        if elem in (OperationLabel.Element.ProperRotation, OperationLabel.Element.ImproperRotation):
            # perpendicular distance to rotation axis (vector rejection)
            return float(np.linalg.norm(coordinates - np.dot(coordinates, self.axis) * self.axis))
        if elem == OperationLabel.Element.Reflection:
            # distance to plane through origin with this normal
            return abs(float(np.dot(self.axis, coordinates)))
        raise RuntimeError("Unexpected symmetry element encountered.")

    # ------------------------------------------------------------------
    # Matrix helpers
    # ------------------------------------------------------------------

    def _calculate_matrix(self, f: float = 1.0) -> np.ndarray:
        """Dispatch to the correct matrix-building method."""
        elem = self.label.element
        if elem == OperationLabel.Element.Inversion:
            return self._calculate_matrix_inversion(f)
        if elem == OperationLabel.Element.ProperRotation:
            return self._calculate_matrix_proper_rotation(f)
        if elem == OperationLabel.Element.ImproperRotation:
            return self._calculate_matrix_improper_rotation(f)
        if elem == OperationLabel.Element.Reflection:
            return self._calculate_matrix_reflection(f)
        raise RuntimeError("Unexpected symmetry element encountered.")

    def _calculate_matrix_inversion(self, f: float) -> np.ndarray:
        """Return the inversion matrix: (1 - 2f) * I.

        At f=1: (1 - 2)*I = -I, which maps (x,y,z) → (-x,-y,-z) — the full
        inversion.  The f parameter is used only for animation (f interpolates
        from identity at 0 to full inversion at 1).
        """
        return np.eye(3, dtype=float) * (1.0 - 2.0 * f)

    def _calculate_matrix_proper_rotation(self, f: float) -> np.ndarray:
        """Return the Rodrigues rotation matrix for angle = 2π/degree * multiple * f.

        Rodrigues' rotation formula
        ---------------------------
        To rotate by angle θ about unit axis û = (ux, uy, uz), the 3×3 matrix is:

            R = cos(θ)·I  +  sin(θ)·[û]×  +  (1-cos(θ))·û⊗û

        where [û]× is the skew-symmetric cross-product matrix and û⊗û is the
        outer product.  Expanding the three terms and collecting by row/column
        gives the explicit form coded below.

        For a Cn operation the rotation angle is 2π/n (one full step).  For the
        k-th power Cn^k it is k·2π/n.  The `multiple` field holds k, so the
        angle is 2π/degree * multiple.

        GLM stores [col][row]; we derive the numpy [row][col] form directly from
        the standard Rodrigues formula so no index transposition is required.
        """
        # An infinite-order axis (C∞) is represented as the identity; it is
        # never applied numerically but must be a valid matrix.
        if self.degree == self.DEGREE_INF:
            return np.eye(3, dtype=float)

        angle = 2.0 * math.pi / self.degree * self.label.multiple * f
        c = math.cos(angle)
        s = math.sin(angle)
        ux, uy, uz = self.axis[0], self.axis[1], self.axis[2]

        # Verified against C++ GLM [col][row] layout:
        # C++ matrix[col][row] -> numpy R[row, col]
        return np.array([
            [ux*ux*(1-c)+c,    ux*uy*(1-c)-uz*s,  ux*uz*(1-c)+uy*s],
            [uy*ux*(1-c)+uz*s, uy*uy*(1-c)+c,     uy*uz*(1-c)-ux*s],
            [uz*ux*(1-c)-uy*s, uz*uy*(1-c)+ux*s,  uz*uz*(1-c)+c   ],
        ], dtype=float)

    def _calculate_matrix_reflection(self, f: float) -> np.ndarray:
        """Return the Householder reflection matrix: I - 2f · outer(n, n).

        To reflect a vector v through the plane with unit normal n:
            v' = v - 2(v·n)n

        In matrix form this is:  R = I - 2·n⊗n  (the Householder matrix).
        np.outer(n, n) computes the 3×3 outer product n⊗n directly.
        The f parameter animates from identity (f=0) to full reflection (f=1).
        """
        return np.eye(3, dtype=float) - 2.0 * f * np.outer(self.axis, self.axis)

    def _calculate_matrix_improper_rotation(self, f: float) -> np.ndarray:
        """Return the improper rotation matrix: reflection @ rotation.

        An improper rotation Sn is defined as a proper rotation Cn followed by
        reflection through the plane perpendicular to the rotation axis.
        In matrix form:  S = σ · R  (matrix multiplication, right-to-left).

        Note that σ and R share the same axis: the plane normal equals the
        rotation axis.  This is why the same self.axis drives both matrices.

        The animation fractions split the motion into two sequential halves:
        rotate first (f from 0→0.5), then reflect (f from 0.5→1).
        At f=1 the combined matrix gives the full Sn operation.
        """
        f_rot = min(2.0 * f, 1.0)        # ramps 0→1 over first half
        f_ref = max(2.0 * f - 1.0, 0.0)  # ramps 0→1 over second half
        rot = self._calculate_matrix_proper_rotation(f_rot)
        ref = self._calculate_matrix_reflection(f_ref)
        return ref @ rot

    def calculate_fractional_matrix(self, f: float) -> np.ndarray:
        """Return the transformation matrix at animation fraction f ∈ [0, 1]."""
        return self._calculate_matrix(f)

    # ------------------------------------------------------------------
    # Geometric atom queries
    # ------------------------------------------------------------------

    def atoms_on_axis(self, structure: Structure, threshold: float = 0.3) -> list[int]:
        """Return indices of atoms within threshold Å of the rotation axis.

        Uses perpendicular distance (vector rejection from the axis direction).
        Only meaningful for ProperRotation and ImproperRotation operations.
        """
        result = []
        for i, coord in enumerate(structure.coordinates):
            proj = np.dot(coord, self.axis)
            perp_dist = float(np.linalg.norm(coord - proj * self.axis))
            if perp_dist < threshold:
                result.append(i)
        return result

    def atoms_in_plane(self, structure: Structure, threshold: float = 0.3) -> list[int]:
        """Return indices of atoms within threshold Å of the mirror plane.

        Uses the signed distance |r · n| where n is the plane normal (self.axis).
        Only meaningful for Reflection operations.
        """
        result = []
        for i, coord in enumerate(structure.coordinates):
            dist = abs(float(np.dot(coord, self.axis)))
            if dist < threshold:
                result.append(i)
        return result

    def is_molecular_plane(self, structure: Structure, threshold: float = 0.3) -> bool:
        """Return True if every atom in structure lies within threshold Å of this plane.

        A True result means this mirror plane is (or contains) the molecular plane —
        relevant for planar molecules where σh coincides with the molecular plane.
        Only meaningful for Reflection operations.
        """
        return len(self.atoms_in_plane(structure, threshold)) == structure.num_atoms
