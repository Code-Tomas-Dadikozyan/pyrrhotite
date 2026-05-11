"""
Symmetry determination pipeline: principal axes, rotor classification,
symmetry-operation search, point-group assignment, Cartesian axis labelling.
Direct translation of reference/src/symmetry/symmetry.h/cpp.
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
        """Build the inertia tensor, diagonalise it, and store moments and axes."""
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

        # eigh returns eigenvalues in ascending order, matching Eigen's SelfAdjointEigenSolver
        eigenvalues, eigenvectors = np.linalg.eigh(I)

        self._principal_moments = eigenvalues   # shape (3,)
        self._principal_axes = eigenvectors     # shape (3,3), columns = principal axes

    def _determine_rotor_class(self) -> None:
        """Classify the rotor type from degeneracy of the sorted principal moments."""
        m = self._principal_moments  # sorted ascending by eigh

        if (m[2] - m[0]) / m[2] < 0.02:
            self._rotor_class = RotorClass.SphericalTop
        elif (m[1] - m[0]) / m[1] < 0.02:
            self._rotor_class = RotorClass.OblateSymmetricTop
        elif (m[2] - m[1]) / m[2] < 0.02:
            if m[0] < 0.02:
                self._rotor_class = RotorClass.Linear
            else:
                self._rotor_class = RotorClass.ProlateSymmetricTop
        else:
            self._rotor_class = RotorClass.AsymmetricTop

    def _axis_inertially_allowed(self, axis: np.ndarray) -> bool:
        """Return True if axis is compatible with the inertial tensor symmetry.

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
            # axis must be parallel or perpendicular to the nondegenerate principal axis
            return dot < 0.02 or dot > 1.0 - 0.02

        if rotor_class == RotorClass.AsymmetricTop:
            min_dot = float("inf")
            for i in range(3):
                principal_axis = self._principal_axes[:, i]
                dot = float(np.dot(principal_axis, axis))
                if dot < min_dot:
                    min_dot = dot
            # faithful translation: no abs() — matches C++ behaviour
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
        """Dispatch proper-rotation search: linear uses C∞ only; others search exhaustively."""
        if self._rotor_class == RotorClass.Linear:
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
        """Test Cn (n=2..8) along the vector from the origin to each atom."""
        for i in range(self._structure.num_atoms):
            axis = self._structure.coordinates[i]
            if float(np.dot(axis, axis)) == 0.0:
                continue
            if not self._axis_inertially_allowed(axis):
                continue
            for degree in range(2, 9):
                op = _Operation.rotation(_OL.Element.ProperRotation, degree, axis)
                self._operation_manager.add_operation(op)

    def _find_proper_rotational_axes_between_atoms(self) -> None:
        """Test Cn (n=2,4,6,8) along midpoints between same-element atom pairs."""
        n = self._structure.num_atoms
        for i in range(n - 1):
            for j in range(i + 1, n):
                if self._structure.atomic_numbers[i] != self._structure.atomic_numbers[j]:
                    continue
                if self._rotor_class == RotorClass.SphericalTop:
                    diff = self._structure.coordinates[i] - self._structure.coordinates[j]
                    if float(np.dot(diff, diff)) > 16.0:
                        continue
                axis = 0.5 * (self._structure.coordinates[i] + self._structure.coordinates[j])
                if float(np.dot(axis, axis)) == 0.0:
                    continue
                if not self._axis_inertially_allowed(axis):
                    continue
                for degree in range(2, 9, 2):
                    op = _Operation.rotation(_OL.Element.ProperRotation, degree, axis)
                    exists = self._operation_manager.add_operation(op)
                    # if C2 is absent, no higher even-degree axis can exist along this direction
                    if degree == 2 and not exists:
                        break

    def _find_proper_rotational_axes_polygonal_faces(self) -> None:
        """For spherical tops, add C3/C5 axes through polygonal faces based on C2 count."""
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
        """Test planes whose normals bisect same-element atom pairs (perpendicular bisector planes)."""
        n = self._structure.num_atoms
        for i in range(n - 1):
            for j in range(i + 1, n):
                if self._structure.atomic_numbers[i] != self._structure.atomic_numbers[j]:
                    continue
                midpoint = 0.5 * (self._structure.coordinates[i] + self._structure.coordinates[j])
                # normal lies in the plane spanned by the two atom vectors, perpendicular to midpoint
                cross_ij = np.cross(self._structure.coordinates[i], self._structure.coordinates[j])
                normal = np.cross(midpoint, cross_ij)
                if float(np.dot(normal, normal)) == 0.0:
                    continue
                if not self._axis_inertially_allowed(normal):
                    continue
                op = _Operation.reflection(normal)
                self._operation_manager.add_operation(op)

    # ------------------------------------------------------------------
    # Pipeline steps — implemented in this prompt
    # ------------------------------------------------------------------

    def _find_point_group(self) -> None:
        """Pick the point group with the smallest non-negative operation surplus."""
        ops = self._operation_manager.get_operations()
        min_diff = float("inf")
        best: PointGroup | None = None
        for pg in POINT_GROUPS:
            diff = pg.compare_to_symmetry_operations(ops)
            if diff >= 0 and diff < min_diff:
                min_diff = diff
                best = pg
        self._point_group = best

    def _find_cartesian_axes(self) -> None:
        """Determine x, y, z Cartesian axes from symmetry and molecular geometry."""
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
        """Set z to the highest-degree proper rotation axis, breaking ties by atom count then principal-axis alignment."""
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
        """Return the unit normal of the best-fitting plane through all atoms via SVD."""
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
        """Label C2' and C2'' axes in dihedral groups."""
        pg_label = self._point_group.get_label()
        for op in self._operation_manager.get_operations():
            lbl = op.get_label()
            if lbl.get_element() != _OL.Element.ProperRotation:
                continue
            if op.get_degree() != 2:
                continue
            if abs(float(np.dot(op.get_axis(), self._z_axis))) > 1.0 - 0.02:
                continue  # C2 along z has no prime label
            if (pg_label.get_class() == _PGL.Class.Dd
                    or pg_label.get_order() % 2 == 1):
                lbl.set_prime(_OL.Prime.Single)
                continue
            # even-n D/Dh: distinguish C2' from C2''
            theta_x = float(np.arccos(np.clip(
                float(np.dot(op.get_axis(), self._x_axis)), -1.0, 1.0
            )))
            divisor = 2.0 * np.pi / pg_label.get_order()
            remainder = float(np.fmod(theta_x, divisor))
            if remainder <= 0.25 * divisor or remainder > 0.75 * divisor:
                lbl.set_prime(_OL.Prime.Single)
            else:
                lbl.set_prime(_OL.Prime.Double)

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
        """Label σh, σv, σd, σv' for cyclic and dihedral groups."""
        pg_label = self._point_group.get_label()
        for op in self._operation_manager.get_operations():
            lbl = op.get_label()
            if lbl.get_element() != _OL.Element.Reflection:
                continue
            if abs(float(np.dot(op.get_axis(), self._z_axis))) > 1.0 - 0.02:
                lbl.set_plane(_OL.Plane.Horizontal)
                continue
            if pg_label.get_class() == _PGL.Class.Dd:
                lbl.set_plane(_OL.Plane.Dihedral)
                continue
            if pg_label.get_order() % 2 == 1:
                lbl.set_plane(_OL.Plane.Vertical)
                continue
            theta_y = float(np.arccos(np.clip(
                float(np.dot(op.get_axis(), self._y_axis)), -1.0, 1.0
            )))
            divisor = 2.0 * np.pi / pg_label.get_order()
            remainder = float(np.fmod(theta_y, divisor))
            if remainder <= 0.25 * divisor or remainder > 0.75 * divisor:
                lbl.set_plane(_OL.Plane.Vertical)
            else:
                if pg_label.get_order() == 2:
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
