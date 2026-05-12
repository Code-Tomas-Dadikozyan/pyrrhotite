"""
Symmetry operation: matrix construction, application to atoms, equality check.
Direct translation of reference/src/symmetry/operations/operation.h/cpp.
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
        self.error: float = float("nan")
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
    # Getters / setters
    # ------------------------------------------------------------------

    def get_id(self) -> int:
        """Return the unique ID assigned by OperationManager."""
        return self.id

    def set_id(self, id: int) -> None:
        """Set the unique ID."""
        self.id = id

    def get_label(self) -> OperationLabel:
        """Return the mutable label of this operation."""
        return self.label

    def set_label(self, label: OperationLabel) -> None:
        """Replace the label."""
        self.label = label

    def get_error(self) -> float:
        """Return the operation error (must call do_operation first)."""
        if math.isnan(self.error):
            raise RuntimeError("Tried to get the error of a symmetry operation before it was computed.")
        return self.error

    def get_degree(self) -> int:
        """Return the rotation degree (0 == infinite)."""
        return self.degree

    def get_axis(self) -> np.ndarray:
        """Return the rotation/reflection axis (unit vector)."""
        return self.axis

    def get_result_index(self, index: int) -> int:
        """Return the atom index that atom `index` maps to under this operation.

        For degree > 2, follows the chain abs(multiple) times using the
        forwards or backwards index map depending on the sign of multiple.
        """
        if self.label.get_multiple() > 0:
            result_indices = self.result_indices_forwards
        else:
            result_indices = self.result_indices_backwards

        result_index = index
        for _ in range(abs(self.label.get_multiple())):
            result_index = result_indices[result_index]
        return result_index

    # ------------------------------------------------------------------
    # Equality
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Two operations are equal if they represent the same geometric element."""
        if not isinstance(other, Operation):
            return NotImplemented
        if self.label.get_element() != other.label.get_element():
            return False
        elem = self.label.get_element()
        if elem == OperationLabel.Element.Inversion:
            return True
        if elem in (OperationLabel.Element.ProperRotation, OperationLabel.Element.ImproperRotation):
            return (
                self.get_degree() == other.get_degree()
                and 1 - abs(float(np.dot(self.axis, other.axis))) < 0.01
            )
        if elem == OperationLabel.Element.Reflection:
            return 1 - abs(float(np.dot(self.axis, other.axis))) < 0.01
        raise RuntimeError("Unexpected symmetry element encountered.")

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    def do_operation(self, structure: Structure) -> None:
        """Apply this operation to all atoms in structure; set error and result_indices."""
        max_error = 0.0
        n = structure.num_atoms
        self.result_indices_forwards = [0] * n
        if self.label.get_degree() > 2:
            self.result_indices_backwards = [0] * n

        for i in range(n):
            after = self.do_atom_operation(structure.coordinates[i])
            closest = structure.find_closest_index(after, int(structure.atomic_numbers[i]))
            distance = float(np.linalg.norm(after - structure.coordinates[closest]))
            dist_to_elem = self._get_distance_to_element(after)
            error = distance / dist_to_elem if dist_to_elem > 1.0 else distance
            if error > max_error:
                max_error = error
            self.result_indices_forwards[i] = closest
            if self.label.get_degree() > 2:
                self.result_indices_backwards[closest] = i

        self.error = max_error

    def do_atom_operation(self, coordinates: np.ndarray) -> np.ndarray:
        """Apply the transformation matrix to a single atom coordinate vector."""
        return self.matrix @ coordinates

    def _get_distance_to_element(self, coordinates: np.ndarray) -> float:
        """Return the distance from coordinates to this operation's symmetry element."""
        elem = self.label.get_element()
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
        elem = self.label.get_element()
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
        """Return the inversion matrix: (1 - 2f) * I."""
        return np.eye(3, dtype=float) * (1.0 - 2.0 * f)

    def _calculate_matrix_proper_rotation(self, f: float) -> np.ndarray:
        """Return the Rodrigues rotation matrix for angle = 2π/degree * multiple * f.

        GLM stores [col][row]; we derive the numpy [row][col] form directly from
        the standard Rodrigues formula so no index transposition is required.
        """
        if self.degree == self.DEGREE_INF:
            return np.eye(3, dtype=float)

        angle = 2.0 * math.pi / self.degree * self.label.get_multiple() * f
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
        """Return the Householder reflection matrix: I - 2f * outer(n, n)."""
        return np.eye(3, dtype=float) - 2.0 * f * np.outer(self.axis, self.axis)

    def _calculate_matrix_improper_rotation(self, f: float) -> np.ndarray:
        """Return the improper rotation matrix: reflection @ rotation.

        The animation fractions split the motion: rotate first (0→0.5),
        then reflect (0.5→1), matching the C++ implementation.
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

    def get_atoms_on_axis(self, structure: Structure, threshold: float = 0.3) -> list[int]:
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

    def get_atoms_in_plane(self, structure: Structure, threshold: float = 0.3) -> list[int]:
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
        return len(self.get_atoms_in_plane(structure, threshold)) == structure.num_atoms
