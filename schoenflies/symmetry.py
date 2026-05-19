"""
Symmetry determination pipeline: principal axes, rotor classification,
symmetry-operation search, point-group assignment, Cartesian axis labelling.
Direct translation of reference/src/symmetry/symmetry.h/cpp.

Algorithm overview
------------------
Given a molecule whose coordinates are centred at the centre of mass, this
module determines the Schoenflies point group in six stages:

  1. _determine_principal_axes
       Build the 3×3 inertia tensor and diagonalise it.  The eigenvectors
       become the principal axes; the eigenvalues (principal moments of
       inertia) classify the rotor type.

  2. _determine_rotor_class
       Compare the three sorted moments to decide whether the molecule is
       a spherical top, linear, symmetric top, or asymmetric top.  This
       constrains which symmetry axes are physically reasonable.

  3. _find_symmetry_operations
       Systematically test candidate symmetry operations (inversion, Cn,
       Sn, σ).  Each candidate is rejected if applying its matrix to every
       atom fails to map all atoms onto atoms of the same element within a
       tolerance.

  4. _find_point_group
       Compare the multiset of valid operations against the hardcoded
       character-table database; fall back to analytical generation for
       high-order axial groups.

  5. _find_cartesian_axes
       Choose a conventional right-handed (x, y, z) frame: z along the
       principal symmetry axis, x toward the most atoms (or in the molecular
       plane), y = z × x.

  6. _label_symmetry_operations
       Assign σh/σv/σd and C2′/C2″ labels based on axis orientations.

Numerical tolerance
-------------------
Most comparisons use 0.02 as the threshold (e.g. |a - b|/|b| < 0.02 for
moment degeneracy, or 1 - |u·v| < 0.02 for axis parallelism).  This is an
empirical value carried over from the reference C++ implementation; it is
loose enough to tolerate finite-precision XYZ coordinates but tight enough
not to confuse distinct axes.
"""

from __future__ import annotations

import numpy as np

from .periodic_table import get_element
from .rotor_class import RotorClass
from .structure import Structure
from .operations.operation import Operation as _Operation
from .operations.operation_label import OperationLabel as _OL
from .operations.operation_manager import OperationManager
from .point_groups.point_group import PointGroup
from .point_groups.point_group_label import PointGroupLabel as _PGL
from .point_groups.point_groups import POINT_GROUPS
from .point_groups.character_table_generator import generate_point_group as _generate_pg


class Symmetry:
    """Runs the full Schoenflies point-group determination pipeline for a Structure."""

    def __init__(self, structure: Structure) -> None:
        """Store structure, build OperationManager, and run all pipeline steps."""
        self._structure: Structure = structure
        self._operation_manager: OperationManager = OperationManager(structure)

        self._principal_moments: np.ndarray = np.zeros(3, dtype=float)
        # columns are eigenvectors (principal axes), matching glm::column(M, i) = M[:, i]
        self._principal_axes: np.ndarray = np.eye(3, dtype=float)

        self._x_axis: np.ndarray = np.full(3, float("nan"))
        self._y_axis: np.ndarray = np.full(3, float("nan"))
        self._z_axis: np.ndarray = np.full(3, float("nan"))

        self._rotor_class: RotorClass = RotorClass.AsymmetricTop
        self._point_group: PointGroup | None = None

        self._determine_principal_axes()
        self._determine_rotor_class()
        self._find_symmetry_operations()
        self._find_point_group()
        self._find_cartesian_axes()
        self._label_symmetry_operations()

        self._operation_manager.generate_point_group_operations(self._point_group)

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------

    def get_structure(self) -> Structure:
        """Return the structure used for this symmetry determination."""
        return self._structure

    def get_principal_moments(self) -> np.ndarray:
        """Return the three principal moments of inertia, sorted ascending."""
        return self._principal_moments

    def get_principal_axes(self) -> np.ndarray:
        """Return the 3x3 matrix whose columns are the principal axes (eigenvectors)."""
        return self._principal_axes

    def get_x_axis(self) -> np.ndarray:
        """Return the Cartesian x axis (set after find_cartesian_axes)."""
        return self._x_axis

    def get_y_axis(self) -> np.ndarray:
        """Return the Cartesian y axis (set after find_cartesian_axes)."""
        return self._y_axis

    def get_z_axis(self) -> np.ndarray:
        """Return the Cartesian z axis (set after find_cartesian_axes)."""
        return self._z_axis

    def get_cartesian_axes(self) -> np.ndarray:
        """Return the 3x3 Cartesian-axis matrix with columns [x, y, z]."""
        return np.column_stack([self._x_axis, self._y_axis, self._z_axis])

    def get_rotor_class(self) -> RotorClass:
        """Return the rotor classification of the structure."""
        return self._rotor_class

    def get_point_group(self) -> PointGroup:
        """Return the determined point group."""
        return self._point_group

    def get_operation_manager(self) -> OperationManager:
        """Return the operation manager holding all found symmetry operations."""
        return self._operation_manager

    # ------------------------------------------------------------------
    # Pipeline steps — implemented in this prompt
    # ------------------------------------------------------------------

    def _determine_principal_axes(self) -> None:
        """Build the inertia tensor, diagonalise it, and store moments and axes.

        The inertia tensor
        ------------------
        The 3×3 inertia tensor I encodes how mass is distributed in space.
        Its diagonal elements (moments of inertia) measure resistance to
        rotation about each axis; its off-diagonal elements (products of
        inertia) measure asymmetry.

        For a collection of point masses mᵢ at positions (xᵢ, yᵢ, zᵢ):

            Ixx = Σ mᵢ (yᵢ² + zᵢ²)   (moment about x axis)
            Ixy = -Σ mᵢ xᵢ yᵢ          (product of inertia, note negative sign)
            … and so on by symmetry.

        I is real and symmetric, so it can always be diagonalised by an
        orthogonal matrix.  The eigenvectors of I are the *principal axes* —
        the special directions in which a rigid body rotates without wobbling.
        The eigenvalues are the *principal moments of inertia* Ia ≤ Ib ≤ Ic.

        Why it matters for symmetry
        ---------------------------
        The principal axes are the natural Cartesian frame for the molecule.
        More importantly, the *pattern of degeneracy* among Ia, Ib, Ic tells
        us what kind of symmetry the molecule can possibly have, allowing the
        algorithm to skip unlikely candidate axes (see _axis_inertially_allowed).
        """
        Ixx = Iyy = Izz = Ixy = Ixz = Iyz = 0.0

        for i in range(self._structure.num_atoms):
            mass = get_element(int(self._structure.atomic_numbers[i])).mass
            x, y, z = self._structure.coordinates[i]

            Ixx += mass * (y * y + z * z)
            Iyy += mass * (x * x + z * z)
            Izz += mass * (x * x + y * y)

            Ixy -= mass * x * y
            Ixz -= mass * x * z
            Iyz -= mass * y * z

        I = np.array([
            [Ixx, Ixy, Ixz],
            [Ixy, Iyy, Iyz],
            [Ixz, Iyz, Izz],
        ], dtype=float)

        # eigh (for Hermitian/symmetric matrices) returns eigenvalues in ascending
        # order and is numerically more stable than the general eig.
        # This matches Eigen's SelfAdjointEigenSolver used in the C++ reference.
        eigenvalues, eigenvectors = np.linalg.eigh(I)

        self._principal_moments = eigenvalues   # shape (3,): Ia ≤ Ib ≤ Ic
        self._principal_axes = eigenvectors     # shape (3,3): columns are the eigenvectors

    def _determine_rotor_class(self) -> None:
        """Classify the rotor type from degeneracy of the sorted principal moments.

        Each condition tests whether two moments are approximately equal by
        checking that their relative difference is below 2%.  The checks are
        ordered from most symmetric (spherical) to least (asymmetric):

            (m[2] - m[0]) / m[2] < 0.02  → all three close → SphericalTop
            (m[1] - m[0]) / m[1] < 0.02  → smallest two close → OblateSymmetricTop
            (m[2] - m[1]) / m[2] < 0.02  → largest two close:
                m[0] < 0.02              → smallest ≈ 0 → Linear (atoms collinear)
                else                     → ProlateSymmetricTop
            else                         → all distinct → AsymmetricTop
        """
        m = self._principal_moments  # sorted ascending by eigh: m[0] ≤ m[1] ≤ m[2]

        if (m[2] - m[0]) / m[2] < 0.02:
            self._rotor_class = RotorClass.SphericalTop
        elif (m[1] - m[0]) / m[1] < 0.02:
            # Ia ≈ Ib < Ic: two equal small moments, one large → disc-like (oblate)
            self._rotor_class = RotorClass.OblateSymmetricTop
        elif (m[2] - m[1]) / m[2] < 0.02:
            if m[0] < 0.02:
                # Ia ≈ 0: all atoms lie on a line — rotating about that line moves
                # no mass, so the moment of inertia about it is zero.
                self._rotor_class = RotorClass.Linear
            else:
                # Ib ≈ Ic > Ia: two equal large moments → cigar-like (prolate)
                self._rotor_class = RotorClass.ProlateSymmetricTop
        else:
            self._rotor_class = RotorClass.AsymmetricTop

    def _axis_inertially_allowed(self, axis: np.ndarray) -> bool:
        """Return True if axis is compatible with the inertial tensor symmetry.

        Physical reasoning
        ------------------
        The inertia tensor constrains which symmetry axes can exist:

        • SphericalTop (Ia = Ib = Ic): every direction is equally valid —
          any axis is allowed.

        • Symmetric tops (OblateSymmetricTop, ProlateSymmetricTop, Linear):
          The molecule has one "special" axis (the non-degenerate principal
          axis) and a family of equivalent axes perpendicular to it.  A Cn
          symmetry axis can only be *parallel* or *perpendicular* to the
          non-degenerate principal axis — any oblique direction would break
          the rotational symmetry of the inertia tensor.

          For an oblate top (Ia = Ib < Ic), the unique axis is the one with
          the *largest* moment (column 2 after ascending sort).
          For a prolate top (Ia < Ib = Ic), the unique axis has the *smallest*
          moment (column 0).

        • AsymmetricTop (Ia < Ib < Ic): all three moments are distinct, so
          symmetry axes can only coincide with the three principal axes
          themselves.  The axis is allowed if its projection onto at least
          one principal axis is nearly zero — i.e. it lies in the plane
          spanned by two principal axes (which includes the axes themselves).

        The 0.02 tolerance (≈ 2%) matches the same threshold used for moment
        degeneracy in _determine_rotor_class.

        Replicates C++ axis_inertially_allowed exactly, including the AsymmetricTop
        branch which uses raw (unnormalised) dot products without abs().
        """
        rotor_class = self._rotor_class

        if rotor_class == RotorClass.SphericalTop:
            return True

        if rotor_class in (
            RotorClass.OblateSymmetricTop,
            RotorClass.ProlateSymmetricTop,
            RotorClass.Linear,
        ):
            if rotor_class == RotorClass.OblateSymmetricTop:
                # nondegenerate axis is the highest moment -> column 2
                nondegenerate = self._principal_axes[:, 2]
            else:
                # ProlateSymmetricTop or Linear: nondegenerate is lowest moment -> column 0
                nondegenerate = self._principal_axes[:, 0]

            dot = float(np.dot(nondegenerate, axis))
            # Accept if axis is nearly parallel (dot > 0.98) or perpendicular (dot < 0.02).
            # Note: axis is assumed to already point roughly in the positive direction;
            # for a normalised axis the dot product with a unit vector is cos(θ).
            return dot < 0.02 or dot > 1.0 - 0.02

        if rotor_class == RotorClass.AsymmetricTop:
            min_dot = float("inf")
            for i in range(3):
                principal_axis = self._principal_axes[:, i]
                dot = float(np.dot(principal_axis, axis))
                if dot < min_dot:
                    min_dot = dot
            # faithful translation: no abs() — matches C++ behaviour.
            # The minimum (signed) dot product being small means the axis is
            # roughly perpendicular to at least one principal axis, i.e. it
            # lives close to the plane spanned by the other two.
            return min_dot < 0.02

        return False

    # ------------------------------------------------------------------
    # Pipeline steps — implemented in this prompt
    # ------------------------------------------------------------------

    def _find_symmetry_operations(self) -> None:
        """Find all symmetry operations: inversion, proper/improper rotations, reflections."""
        self._find_inversion_centre()
        self._find_proper_rotational_axes()
        self._find_improper_rotational_axes()
        self._find_reflection_planes()

    def _find_inversion_centre(self) -> None:
        """Test and (if valid) register an inversion centre."""
        op = _Operation.inversion()
        self._operation_manager.add_operation(op)

    def _find_proper_rotational_axes(self) -> None:
        """Dispatch proper-rotation search: linear uses C∞ only; others search exhaustively.

        Three complementary search strategies ensure no axis is missed:

        1. Along principal axes — always a starting point because the inertia
           tensor eigenvectors are natural candidates for symmetry axes.

        2. Through atoms — an atom lying exactly on a Cn axis must map to
           itself under Cn, so the atom-to-origin vector is always a candidate.

        3. Between atoms (midpoints) — for even-order axes such as C2, the
           axis may bisect a pair of equivalent atoms; neither individual atom
           lies on the axis, but their midpoint does.

        For spherical tops (e.g. cubane, fullerene) a fourth search through
        polygonal face normals is required because the C3/C5 axes do not
        necessarily pass through atoms or their midpoints.
        """
        if self._rotor_class == RotorClass.Linear:
            # Linear molecules have a single C∞ axis along the molecular axis
            # (the lowest-moment principal axis, column 0).
            axis = self._principal_axes[:, 0]
            op = _Operation.rotation(_OL.Element.ProperRotation, _Operation.DEGREE_INF, axis)
            self._operation_manager.add_operation(op)
        else:
            self._find_proper_rotational_axes_along_principal_axes()
            self._find_proper_rotational_axes_through_atoms()
            self._find_proper_rotational_axes_between_atoms()
            if self._rotor_class == RotorClass.SphericalTop:
                self._find_proper_rotational_axes_polygonal_faces()

    def _find_proper_rotational_axes_along_principal_axes(self) -> None:
        """Test Cn (n=2..8) along each of the three principal axes."""
        for i in range(3):
            axis = self._principal_axes[:, i]
            for degree in range(2, 9):
                op = _Operation.rotation(_OL.Element.ProperRotation, degree, axis)
                self._operation_manager.add_operation(op)

    def _find_proper_rotational_axes_through_atoms(self) -> None:
        """Test Cn (n=2..8) along the vector from the origin to each atom.

        If a Cn axis passes through an atom, that atom must map to itself
        (it is on the axis), so the origin-to-atom direction is a candidate.
        Atoms at the origin (the COM) are skipped since they give a zero vector.
        The inertial-allowed filter skips directions incompatible with the
        molecule's overall shape before the more expensive matrix test.
        """
        for i in range(self._structure.num_atoms):
            axis = self._structure.coordinates[i]
            if float(np.dot(axis, axis)) == 0.0:
                continue  # atom is at the centre of mass — no direction to test
            if not self._axis_inertially_allowed(axis):
                continue
            for degree in range(2, 9):
                op = _Operation.rotation(_OL.Element.ProperRotation, degree, axis)
                self._operation_manager.add_operation(op)

    def _find_proper_rotational_axes_between_atoms(self) -> None:
        """Test Cn (n=2,4,6,8) along midpoints between same-element atom pairs.

        Why midpoints?
        --------------
        A C2 axis exchanges two equivalent atoms: each maps to the other.
        The axis must then pass through the midpoint of the two atom positions
        (the only point equidistant from both).  Similarly for C4, C6, C8.
        Odd-order axes (C3, C5, C7) cannot exchange pairs — they cycle atoms
        in groups of 3/5/7 — so only even degrees are tested here.

        Only same-element pairs are tested: a rotation can only map atom i to
        atom j if they are the same element (same atomic number).

        The SphericalTop distance cutoff (dist² < 16 Å²) limits the pair
        search to nearby atoms in large cage molecules, where the quadratic
        number of pairs would otherwise be prohibitively large.

        Early termination: if C2 does not exist along a given midpoint axis,
        no higher even-order axis (C4, C6, C8) can exist there either, because
        Cn^(n/2) = C2 — so we stop as soon as C2 fails.
        """
        n = self._structure.num_atoms
        for i in range(n - 1):
            for j in range(i + 1, n):
                if self._structure.atomic_numbers[i] != self._structure.atomic_numbers[j]:
                    continue
                if self._rotor_class == RotorClass.SphericalTop:
                    diff = self._structure.coordinates[i] - self._structure.coordinates[j]
                    if float(np.dot(diff, diff)) > 16.0:
                        continue  # atoms too far apart for spherical top search
                axis = 0.5 * (self._structure.coordinates[i] + self._structure.coordinates[j])
                if float(np.dot(axis, axis)) == 0.0:
                    continue  # midpoint is at the origin — degenerate case
                if not self._axis_inertially_allowed(axis):
                    continue
                for degree in range(2, 9, 2):
                    op = _Operation.rotation(_OL.Element.ProperRotation, degree, axis)
                    exists = self._operation_manager.add_operation(op)
                    # if C2 is absent, no higher even-degree axis can exist along this direction
                    if degree == 2 and not exists:
                        break

    def _find_proper_rotational_axes_polygonal_faces(self) -> None:
        """For spherical tops, add C3/C5 axes through polygonal faces based on C2 count.

        Tetrahedral (T), octahedral (O), and icosahedral (I) molecules have
        characteristic counts of C2 axes that identify the family:
            3  C2 axes → T symmetry  → C3 axes through triangular faces
            9  C2 axes → O symmetry  → C3 axes through triangular faces
           15  C2 axes → I symmetry  → C3 and C5 axes through polygonal faces

        For T/O groups, the C3 axes point toward the vertices of a cube aligned
        with the principal axes — they are the ±x±y±z directions (eight diagonal
        directions, tested in the helper function).

        For I groups, the C3 and C5 axes are normal to triangular and pentagonal
        faces; since the faces are not aligned with any simple direction, they are
        found by taking cross products of pairs of known C2 axes.
        """
        c2s = [
            op for op in self._operation_manager.get_operations()
            if op.get_label().get_element() == _OL.Element.ProperRotation
            and op.get_degree() == 2
        ]
        n_c2 = len(c2s)
        if n_c2 in (3, 9):
            self._find_proper_rotational_axes_polygonal_faces_T_O()
        elif n_c2 == 15:
            self._find_proper_rotational_axes_polygonal_faces_I(c2s)

    def _find_proper_rotational_axes_polygonal_faces_T_O(self) -> None:
        """For T/O symmetry: C3 axes are sums of +/-1 combinations of the three principal axes."""
        for i in (-1, 1):
            for j in (-1, 1):
                axis = (
                    self._principal_axes[:, 0] * float(i)
                    + self._principal_axes[:, 1] * float(j)
                    + self._principal_axes[:, 2]
                )
                op = _Operation.rotation(_OL.Element.ProperRotation, 3, axis)
                self._operation_manager.add_operation(op)

    def _find_proper_rotational_axes_polygonal_faces_I(
        self, c2s: list,
    ) -> None:
        """For I symmetry: C3 and C5 axes are cross products of C2-axis pairs."""
        for i in range(len(c2s) - 1):
            for j in range(i + 1, len(c2s)):
                axis = np.cross(c2s[i].get_axis(), c2s[j].get_axis())
                if float(np.dot(axis, axis)) == 0.0:
                    continue
                for degree in (3, 5):
                    op = _Operation.rotation(_OL.Element.ProperRotation, degree, axis)
                    self._operation_manager.add_operation(op)

    def _find_improper_rotational_axes(self) -> None:
        """Add Sn axes coincident with all found Cn axes; degree = n or 2n (min degree 3)."""
        if self._rotor_class == RotorClass.Linear:
            axis = self._principal_axes[:, 0]
            op = _Operation.rotation(_OL.Element.ImproperRotation, _Operation.DEGREE_INF, axis)
            self._operation_manager.add_operation(op)
            return

        for existing in list(self._operation_manager.get_operations()):
            if existing.get_label().get_element() != _OL.Element.ProperRotation:
                continue
            for degree_factor in (1, 2):
                degree = existing.get_degree() * degree_factor
                if degree <= 2:
                    continue  # S1 = σ, S2 = i; handled separately
                op = _Operation.rotation(_OL.Element.ImproperRotation, degree, existing.get_axis())
                self._operation_manager.add_operation(op)

    def _find_reflection_planes(self) -> None:
        """Search for all reflection planes; skip for linear molecules."""
        if self._rotor_class == RotorClass.Linear:
            return  # infinite σv planes in C∞v/D∞h are not tracked here

        octahedral_or_icosahedral = False
        if self._rotor_class == RotorClass.SphericalTop:
            n_c2 = sum(
                1 for op in self._operation_manager.get_operations()
                if op.get_label().get_element() == _OL.Element.ProperRotation
                and op.get_degree() == 2
            )
            if n_c2 in (9, 15):
                octahedral_or_icosahedral = True

        if not octahedral_or_icosahedral:
            self._find_reflection_planes_normal_to_principal_axes()
        self._find_reflection_planes_normal_to_proper_rotational_axes(octahedral_or_icosahedral)
        if not octahedral_or_icosahedral:
            self._find_reflection_planes_in_midpoints()

    def _find_reflection_planes_normal_to_principal_axes(self) -> None:
        """Test a reflection plane with normal along each principal axis."""
        for i in range(3):
            normal = self._principal_axes[:, i]
            op = _Operation.reflection(normal)
            self._operation_manager.add_operation(op)

    def _find_reflection_planes_normal_to_proper_rotational_axes(
        self, only_c2s: bool
    ) -> None:
        """Test reflection planes whose normals coincide with proper rotation axes."""
        for existing in self._operation_manager.get_operations():
            if existing.get_label().get_element() != _OL.Element.ProperRotation:
                continue
            if only_c2s and existing.get_degree() != 2:
                continue
            op = _Operation.reflection(existing.get_axis())
            self._operation_manager.add_operation(op)

    def _find_reflection_planes_in_midpoints(self) -> None:
        """Test planes whose normals bisect same-element atom pairs (perpendicular bisector planes).

        Why midpoint bisectors?
        -----------------------
        A mirror plane σ swaps two equivalent atoms i and j if the plane passes
        through their midpoint and is *perpendicular to the line joining them*.
        For atoms i and j with position vectors rᵢ and rⱼ:
            midpoint  m  = ½(rᵢ + rⱼ)
            bond direction = rᵢ - rⱼ

        The perpendicular bisector plane contains the midpoint and is normal to
        the bond direction.  However, a molecular mirror plane must also pass
        through the origin (the centre of mass), so we need the plane through
        the origin that contains the midpoint vector.

        Construction:
            1. cross_ij  = rᵢ × rⱼ  (perpendicular to the plane containing
                                       both atoms and the origin)
            2. normal    = m × cross_ij  (perpendicular to both midpoint and
                                          cross_ij, i.e. within the plane of the
                                          atoms and through the origin)

        The result is the normal to a candidate mirror plane that would reflect
        atom i onto atom j (and vice versa) while passing through the origin.
        """
        n = self._structure.num_atoms
        for i in range(n - 1):
            for j in range(i + 1, n):
                if self._structure.atomic_numbers[i] != self._structure.atomic_numbers[j]:
                    continue
                midpoint = 0.5 * (self._structure.coordinates[i] + self._structure.coordinates[j])
                # cross_ij is perpendicular to the plane containing rᵢ, rⱼ, and the origin.
                cross_ij = np.cross(self._structure.coordinates[i], self._structure.coordinates[j])
                # normal is then perpendicular to both midpoint and cross_ij.
                normal = np.cross(midpoint, cross_ij)
                if float(np.dot(normal, normal)) == 0.0:
                    continue  # degenerate case (atoms and origin are collinear)
                if not self._axis_inertially_allowed(normal):
                    continue
                op = _Operation.reflection(normal)
                self._operation_manager.add_operation(op)

    # ------------------------------------------------------------------
    # Pipeline steps — implemented in this prompt
    # ------------------------------------------------------------------

    def _find_point_group(self) -> None:
        """Pick the point group with the smallest non-negative operation surplus.

        Matching strategy
        -----------------
        Each entry in POINT_GROUPS describes the expected set of symmetry
        operations for a known point group.  compare_to_symmetry_operations()
        returns:

            surplus = (operations the group requires) - (operations we found)

        A surplus ≥ 0 means all required operations were found (the group is
        a candidate); a negative surplus means we are missing required operations
        (not this group).  Among all candidates, we pick the one with the
        *smallest* surplus — the tightest fit to the operations actually present.

        Fallback generation
        -------------------
        If no hardcoded group matches (e.g. a C15v molecule), the algorithm
        infers the group class from the operation counts and calls the analytical
        character-table generator.  This handles arbitrarily high-order groups.
        """
        ops = self._operation_manager.get_operations()
        min_diff = float("inf")
        best: PointGroup | None = None
        for pg in POINT_GROUPS:
            diff = pg.compare_to_symmetry_operations(ops)
            if diff >= 0 and diff < min_diff:
                min_diff = diff
                best = pg
        if best is None:
            best = self._generate_point_group_from_ops(ops)
        self._point_group = best

    def _generate_point_group_from_ops(
        self, ops: list
    ) -> PointGroup | None:
        """Infer an axial point-group label from the detected operations and generate it.

        Used when no match is found in the hardcoded POINT_GROUPS list.
        """
        # Count operation types
        n_inv = sum(1 for op in ops
                    if op.get_label().get_element() == _OL.Element.Inversion)
        n_ref = sum(1 for op in ops
                    if op.get_label().get_element() == _OL.Element.Reflection)
        n_impr = sum(1 for op in ops
                     if op.get_label().get_element() == _OL.Element.ImproperRotation)

        # Highest-order proper rotation axis
        proper_degs = [op.get_degree() for op in ops
                       if op.get_label().get_element() == _OL.Element.ProperRotation]
        if not proper_degs:
            return None
        n = max(proper_degs)

        # Count C2 operations (potential C2' axes perpendicular to Cn)
        n_c2 = sum(1 for op in ops
                   if op.get_label().get_element() == _OL.Element.ProperRotation
                   and op.get_degree() == 2)
        # Subtract one C2 if it belongs to the main Cn axis (n even → C2 = Cn^(n/2))
        n_c2_prime = n_c2 - (1 if n % 2 == 0 else 0)

        has_c2_prime = n_c2_prime >= n   # at least n perpendicular C2 axes
        has_sigma_h = any(
            op.get_label().get_element() == _OL.Element.Reflection
            and op.get_label().get_plane() == _OL.Plane.Horizontal
            for op in ops
        )
        has_sigma_v_or_d = any(
            op.get_label().get_element() == _OL.Element.Reflection
            and op.get_label().get_plane() in (_OL.Plane.Vertical, _OL.Plane.Dihedral)
            for op in ops
        )

        try:
            if has_c2_prime and (has_sigma_h or n_inv > 0):
                pg_class = _PGL.Class.Dh
            elif has_c2_prime and has_sigma_v_or_d:
                pg_class = _PGL.Class.Dh
            elif has_c2_prime:
                pg_class = _PGL.Class.D
            elif has_sigma_h and has_sigma_v_or_d:
                pg_class = _PGL.Class.Dh
            elif has_sigma_h:
                pg_class = _PGL.Class.Ch
            elif has_sigma_v_or_d:
                pg_class = _PGL.Class.Cv
            elif n_impr > 0 and n_inv > 0 and not has_sigma_v_or_d:
                # S_{2n} with inversion — check if it's Sn or Dnd
                pg_class = _PGL.Class.S
            elif n_impr > 0:
                pg_class = _PGL.Class.Dd
            else:
                pg_class = _PGL.Class.C
            return _generate_pg(_PGL(pg_class, n))
        except (ValueError, Exception):
            return None

    def _find_cartesian_axes(self) -> None:
        """Determine x, y, z Cartesian axes from symmetry and molecular geometry.

        Convention
        ----------
        The Schoenflies convention places:
            z — along the highest-order proper rotation axis (the "principal axis")
            x — in the plane containing z and the most atoms (or, for planar
                molecules, perpendicular to the molecular plane if z is in-plane)
            y = z × x  (completing a right-handed frame)

        This choice is arbitrary in many cases — the group's symmetry properties
        don't depend on it — but it makes character tables and mode assignments
        match the textbook tables that students and practitioners expect.

        For spherical tops (no single principal axis) or molecules with no
        proper rotation axes at all, the principal axes of inertia are used
        directly to orient the frame.
        """
        num_rotations = sum(
            1 for op in self._operation_manager.get_operations()
            if op.get_label().get_element() == _OL.Element.ProperRotation
        )

        if self._rotor_class == RotorClass.SphericalTop or num_rotations == 0:
            self._assign_principal_axes_to_cartesian_xz()
        else:
            self._find_z_axis()
            if self._structure.num_atoms >= 3:
                plane_normal = self._find_plane_normal()
                if self._structure_is_planar(plane_normal):
                    self._find_x_axis_planar(plane_normal)
                else:
                    self._find_x_axis_not_planar()
            else:
                self._pick_arbitrary_x_axis()

        self._orthonormalise_xz_axes()
        self._find_y_axis()

    def _assign_principal_axes_to_cartesian_xz(self) -> None:
        """Use the lowest-moment principal axis as z, next as x (spherical/nonaxial)."""
        self._z_axis = self._principal_axes[:, 0].copy()
        self._x_axis = self._principal_axes[:, 1].copy()

    def _find_z_axis(self) -> None:
        """Set z to the highest-degree proper rotation axis, breaking ties by atom count then principal-axis alignment.

        The z axis is the "principal axis" — the unique high-symmetry direction
        for axial groups (Cn, Cnv, Cnh, Dn, etc.).  Tie-breaking ensures a
        reproducible choice when multiple axes share the highest degree:
        1. Prefer the axis that more atoms lie on (most constrained direction).
        2. Among those, prefer the axis most parallel to a principal axis
           (minimises floating-point arbitrary choices from nearly-degenerate
           eigenvectors).
        """
        if self._rotor_class == RotorClass.SphericalTop:
            return

        ops = self._operation_manager.get_operations()
        max_degree = max(
            (op.get_degree() for op in ops
             if op.get_label().get_element() == _OL.Element.ProperRotation),
            default=0,
        )
        if max_degree == 0:
            return

        candidates = [
            op.get_axis() for op in ops
            if op.get_label().get_element() == _OL.Element.ProperRotation
            and op.get_degree() == max_degree
        ]

        if len(candidates) == 1:
            self._z_axis = candidates[0].copy()
            return

        # break tie: most atom intersections
        def count_intersections(axis: np.ndarray) -> int:
            n_unit = axis / np.linalg.norm(axis)
            count = 0
            for coord in self._structure.coordinates:
                norm_c = np.linalg.norm(coord)
                if norm_c == 0.0:
                    continue
                dot = abs(float(np.dot(n_unit, coord / norm_c)))
                if dot > 1.0 - 0.02:
                    count += 1
            return count

        intersections = [count_intersections(ax) for ax in candidates]
        max_isect = max(intersections)
        candidates2 = [ax for ax, n in zip(candidates, intersections) if n == max_isect]

        if len(candidates2) == 1:
            self._z_axis = candidates2[0].copy()
            return
        if len(candidates2) == 0:
            return

        # final tie-break: most parallel to any principal axis
        best_idx = 0
        best_diff = float("inf")
        for i, ax in enumerate(candidates2):
            this_min = min(
                1.0 - abs(float(np.dot(ax, self._principal_axes[:, j])))
                for j in range(3)
            )
            if this_min < best_diff:
                best_diff = this_min
                best_idx = i
        self._z_axis = candidates2[best_idx].copy()

    def _find_plane_normal(self) -> np.ndarray:
        """Return the unit normal of the best-fitting plane through all atoms via SVD.

        The coordinates form a (3 × N) matrix.  Its singular value decomposition
        produces left singular vectors U whose columns span the directions of
        maximum variance (descending).  The *last* column of U corresponds to the
        direction of *minimum* variance — i.e. the direction perpendicular to the
        plane in which the atoms are most nearly coplanar.  This is the plane
        normal we want.
        """
        # coords shape (3, N); SVD of coords.T gives U with singular values descending
        coords = self._structure.coordinates.T  # (3, N)
        U, _s, _Vt = np.linalg.svd(coords, full_matrices=False)
        # smallest singular value is the last column of U (descending order)
        return U[:, -1]

    def _structure_is_planar(self, plane_normal: np.ndarray) -> bool:
        """Return True if the mean atom-to-plane distance is below 0.02 Å."""
        total = sum(
            abs(float(np.dot(plane_normal, coord)))
            for coord in self._structure.coordinates
        )
        return total / self._structure.num_atoms < 0.02

    def _find_x_axis_planar(self, plane_normal: np.ndarray) -> None:
        """Choose x axis for a planar structure given the best-fitting plane normal."""
        dot_zn = float(np.dot(plane_normal, self._z_axis))
        if dot_zn > 1.0 - 0.02:
            # z perpendicular to plane → x lies in the plane, through most atoms
            best_axis = np.zeros(3)
            max_count = 0
            for coord in self._structure.coordinates:
                norm_c = np.linalg.norm(coord)
                if norm_c == 0.0:
                    continue
                axis = coord / norm_c
                if abs(float(np.dot(axis, plane_normal))) > 0.02:
                    continue  # not in plane
                count = sum(
                    1 for c in self._structure.coordinates
                    if np.linalg.norm(c) > 0.0
                    and abs(float(np.dot(axis, c / np.linalg.norm(c)))) > 1.0 - 0.02
                )
                if count > max_count:
                    max_count = count
                    best_axis = axis
            self._x_axis = best_axis
        else:
            # z lies in plane → x is perpendicular to plane
            self._x_axis = plane_normal.copy()

    def _find_x_axis_not_planar(self) -> None:
        """Choose x such that the xz-plane contains the most atoms."""
        best_axis = np.zeros(3)
        max_count = 0
        for coord in self._structure.coordinates:
            norm_c = np.linalg.norm(coord)
            if norm_c < 0.02:
                continue  # atom at origin
            axis = coord / norm_c
            if abs(float(np.dot(self._z_axis, axis))) > 1.0 - 0.02:
                continue  # atom on z axis
            plane_n = np.cross(self._z_axis, axis)
            plane_n = plane_n / np.linalg.norm(plane_n)
            count = sum(
                1 for c in self._structure.coordinates
                if np.linalg.norm(c) > 0.0
                and abs(float(np.dot(plane_n, c / np.linalg.norm(c)))) < 0.02
            )
            if count > max_count:
                max_count = count
                best_axis = axis
        self._x_axis = best_axis

    def _pick_arbitrary_x_axis(self) -> None:
        """Pick an arbitrary x axis orthogonal to z (for diatomics/single atoms)."""
        if abs(self._z_axis[1]) < 0.01 or abs(self._z_axis[2]) < 0.01:
            self._x_axis = np.array([1.0, 0.0, 0.0])
        else:
            self._x_axis = np.array([0.0, 1.0, 0.0])

    def _orthonormalise_xz_axes(self) -> None:
        """Gram-Schmidt: normalise z, then remove z-component from x and normalise."""
        self._z_axis = self._z_axis / np.linalg.norm(self._z_axis)
        self._x_axis = self._x_axis - float(np.dot(self._z_axis, self._x_axis)) * self._z_axis
        self._x_axis = self._x_axis / np.linalg.norm(self._x_axis)

    def _find_y_axis(self) -> None:
        """Set y = z × x (right-handed coordinate system)."""
        self._y_axis = np.cross(self._z_axis, self._x_axis)

    def _label_symmetry_operations(self) -> None:
        """Label proper rotations and reflection planes based on point group and axes."""
        self._label_proper_rotational_axes()
        self._label_reflection_planes()

    def _label_proper_rotational_axes(self) -> None:
        """Dispatch rotation labelling for dihedral and octahedral groups."""
        label = self._point_group.get_label()
        if label.is_dihedral():
            self._label_proper_rotational_axes_dihedral()
        if label.is_octahedral():
            self._label_proper_rotational_axes_octahedral()

    def _label_proper_rotational_axes_dihedral(self) -> None:
        """Label C2' and C2'' axes in dihedral groups.

        In a dihedral group Dn (or Dnh / Dnd), there are n horizontal C2 axes
        perpendicular to the principal Cn axis.  When n is even, these split
        into two sets of n/2 axes that are geometrically inequivalent:
            C2′  axes pass through opposite vertices / atoms
            C2″  axes bisect the angles between C2′ axes (pass through edge
                  midpoints for a regular n-gon)

        When n is odd, all n horizontal C2 axes are equivalent (all labelled C2′).
        Dnd groups also use C2′ only (the C2 axes bisect adjacent σd planes).

        Assignment method
        -----------------
        For even-n D/Dh groups, the angle θ between a C2 axis and the x axis
        is compared to the fundamental angular step 2π/n.  An axis that falls
        in the first or last quarter of that step is labelled C2′ (aligned
        with x); one in the middle half is labelled C2″ (midway between).
        """
        pg_label = self._point_group.get_label()
        for op in self._operation_manager.get_operations():
            lbl = op.get_label()
            if lbl.get_element() != _OL.Element.ProperRotation:
                continue
            if op.get_degree() != 2:
                continue
            if abs(float(np.dot(op.get_axis(), self._z_axis))) > 1.0 - 0.02:
                continue  # C2 along z is the main axis — no prime label
            if (pg_label.get_class() == _PGL.Class.Dd
                    or pg_label.get_order() % 2 == 1):
                # All horizontal C2 axes are equivalent — label them all C2′.
                lbl.set_prime(_OL.Prime.Single)
                continue
            # even-n D/Dh: distinguish C2' from C2'' by angular position relative to x
            theta_x = float(np.arccos(np.clip(
                float(np.dot(op.get_axis(), self._x_axis)), -1.0, 1.0
            )))
            divisor = 2.0 * np.pi / pg_label.get_order()
            remainder = float(np.fmod(theta_x, divisor))
            if remainder <= 0.25 * divisor or remainder > 0.75 * divisor:
                lbl.set_prime(_OL.Prime.Single)   # close to x → C2′
            else:
                lbl.set_prime(_OL.Prime.Double)   # midway between → C2″

    def _label_proper_rotational_axes_octahedral(self) -> None:
        """Label C2' axes in octahedral groups (those not parallel to a principal axis)."""
        for op in self._operation_manager.get_operations():
            lbl = op.get_label()
            if lbl.get_element() != _OL.Element.ProperRotation:
                continue
            if op.get_degree() != 2:
                continue
            parallel = any(
                abs(float(np.dot(op.get_axis(), self._principal_axes[:, j]))) > 1.0 - 0.02
                for j in range(3)
            )
            if not parallel:
                lbl.set_prime(_OL.Prime.Single)

    def _label_reflection_planes(self) -> None:
        """Dispatch reflection-plane labelling by point group class."""
        pg_class = self._point_group.get_label().get_class()
        if pg_class in (
            _PGL.Class.Cv, _PGL.Class.Ch, _PGL.Class.Cs,
            _PGL.Class.Dh, _PGL.Class.Dd,
        ):
            self._label_reflection_planes_cyclic_dihedral()
        elif pg_class in (_PGL.Class.Td, _PGL.Class.Th):
            self._label_reflection_planes_tetrahedral()
        elif pg_class == _PGL.Class.Oh:
            self._label_reflection_planes_octahedral()

    def _label_reflection_planes_cyclic_dihedral(self) -> None:
        """Label σh, σv, σd, σv' for cyclic and dihedral groups.

        A plane whose normal is nearly parallel to z is σh (horizontal — it
        lies perpendicular to the principal axis).

        Vertical planes (containing z) are further sub-classified:
            σv — contains the principal axis AND at least one atom (or a C2′ axis)
            σd — contains the principal axis but bisects adjacent C2′ axes

        For Dnd groups, all vertical planes are σd by definition.
        For odd-order groups there is only one set (labelled σv).
        For even-order groups, the angular position relative to y distinguishes
        σv from σd by the same half-step test used for C2′/C2″.
        """
        pg_label = self._point_group.get_label()
        for op in self._operation_manager.get_operations():
            lbl = op.get_label()
            if lbl.get_element() != _OL.Element.Reflection:
                continue
            # A plane is horizontal if its normal is parallel to z.
            if abs(float(np.dot(op.get_axis(), self._z_axis))) > 1.0 - 0.02:
                lbl.set_plane(_OL.Plane.Horizontal)
                continue
            if pg_label.get_class() == _PGL.Class.Dd:
                lbl.set_plane(_OL.Plane.Dihedral)
                continue
            if pg_label.get_order() % 2 == 1:
                # Odd-order groups have a single type of vertical plane.
                lbl.set_plane(_OL.Plane.Vertical)
                continue
            # For even-order groups, use angular position relative to y to distinguish σv/σd.
            theta_y = float(np.arccos(np.clip(
                float(np.dot(op.get_axis(), self._y_axis)), -1.0, 1.0
            )))
            divisor = 2.0 * np.pi / pg_label.get_order()
            remainder = float(np.fmod(theta_y, divisor))
            if remainder <= 0.25 * divisor or remainder > 0.75 * divisor:
                lbl.set_plane(_OL.Plane.Vertical)
            else:
                if pg_label.get_order() == 2:
                    # C2v special case: two vertical planes, label the second σv′
                    lbl.set_plane(_OL.Plane.Vertical)
                    lbl.set_prime(_OL.Prime.Single)
                else:
                    lbl.set_plane(_OL.Plane.Dihedral)

    def _label_reflection_planes_tetrahedral(self) -> None:
        """Label all planes σd (Td) or σh (Th)."""
        pg_class = self._point_group.get_label().get_class()
        if pg_class == _PGL.Class.Td:
            plane = _OL.Plane.Dihedral
        elif pg_class == _PGL.Class.Th:
            plane = _OL.Plane.Horizontal
        else:
            raise RuntimeError("Unexpected point group class in tetrahedral labelling.")
        for op in self._operation_manager.get_operations():
            if op.get_label().get_element() == _OL.Element.Reflection:
                op.get_label().set_plane(plane)

    def _label_reflection_planes_octahedral(self) -> None:
        """Label planes σh (parallel to a principal axis) or σd."""
        for op in self._operation_manager.get_operations():
            lbl = op.get_label()
            if lbl.get_element() != _OL.Element.Reflection:
                continue
            parallel = any(
                abs(float(np.dot(op.get_axis(), self._principal_axes[:, j]))) > 1.0 - 0.02
                for j in range(3)
            )
            lbl.set_plane(_OL.Plane.Horizontal if parallel else _OL.Plane.Dihedral)
