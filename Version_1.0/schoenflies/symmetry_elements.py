"""
symmetry_elements.py — SymmetryFinder class

Searches for all symmetry elements present in a molecule:
  - Inversion centre (i)
  - Proper rotation axes (Cn, n = 2..8)
  - Mirror planes (σ)
  - Improper rotation axes (Sn)

The search is guided by the molecule's rotor class (computed in molecule.py)
to avoid testing physically impossible symmetry elements.  Each element is
found by applying the operation to the full set of atomic coordinates and
checking whether every transformed atom lands on top of an equivalent atom.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field

from .utils import (
    GEOMETRY_TOLERANCE,
    rotation_matrix,
    reflection_matrix,
    apply_matrix,
    are_equivalent,
    axes_are_parallel,
    plane_normal,
)
from .molecule import (
    Molecule,
    ROTOR_LINEAR,
    ROTOR_SPHERICAL_TOP,
    ROTOR_PROLATE_SYMMETRIC,
    ROTOR_OBLATE_SYMMETRIC,
    ROTOR_ASYMMETRIC,
)

# Maximum Cn order the algorithm will search for.
# The C++ source also caps at 8; n=9 and above are essentially unobserved
# in stable molecules and would make the search significantly slower.
MAX_CN_ORDER = 8

# Tolerance (in radians, approximately) used when deciding whether two
# axis DIRECTIONS are "the same".  Larger than GEOMETRY_TOLERANCE because
# we are comparing angles between vectors, not atom positions.
AXIS_PARALLEL_TOL = 0.1   # ≈ 5.7°


# ---------------------------------------------------------------------------
# Data structures for found symmetry elements
# ---------------------------------------------------------------------------

@dataclass
class RotationAxis:
    """A proper rotation axis Cn of order n.

    Chemistry: a Cn axis means rotating the molecule by 360°/n about `axis`
    maps it onto itself.  A C6 in benzene means a 60° rotation is a symmetry
    operation.
    """
    axis: np.ndarray   # unit vector (3,)
    order: int         # n in Cn


@dataclass
class ReflectionPlane:
    """A mirror plane σ, defined by its unit normal vector.

    Chemistry: reflecting every atom through the plane maps the molecule
    onto itself.  The plane passes through the origin (the centre of mass).
    """
    normal: np.ndarray  # unit vector (3,) perpendicular to the plane


@dataclass
class ImproperAxis:
    """An improper rotation axis Sn of order n.

    Chemistry: Sn = rotation by 360°/n about `axis` followed by reflection
    through the plane perpendicular to `axis`.  S1 = σ, S2 = i, S4 in allene,
    S6 in staggered ethane, S8 in octasulfur.
    """
    axis: np.ndarray   # unit vector (3,)
    order: int         # n in Sn


# ---------------------------------------------------------------------------
# SymmetryFinder
# ---------------------------------------------------------------------------

class SymmetryFinder:
    """
    Detects all symmetry elements for a given Molecule.

    Usage
    -----
        mol = Molecule('water.xyz')
        sf  = SymmetryFinder(mol)
        sf.find_all()
        print(sf.has_inversion)       # False
        print(sf.count_cn(2))         # 1   (the C2 axis)
        print(sf.count_sigma())       # 2   (σv planes)

    The typical call sequence mirrors the C++ source:
        find_inversion_centre()
        find_proper_rotational_axes()
        find_reflection_planes()
        find_improper_rotational_axes()
    """

    def __init__(self, molecule: Molecule) -> None:
        self.molecule = molecule

        # Results — populated by the find_* methods
        self.has_inversion: bool = False
        self.proper_axes:      list[RotationAxis]   = []
        self.reflection_planes: list[ReflectionPlane] = []
        self.improper_axes:    list[ImproperAxis]   = []

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def find_all(self) -> None:
        """Run the full symmetry search in the same order as the C++ source."""
        self.find_inversion_centre()
        self.find_proper_rotational_axes()
        self.find_reflection_planes()
        self.find_improper_rotational_axes()

    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------

    def count_cn(self, n: int) -> int:
        """Return the number of distinct Cn axes of order exactly n."""
        return sum(1 for ax in self.proper_axes if ax.order == n)

    def has_cn(self, n: int) -> bool:
        return self.count_cn(n) > 0

    def max_cn_order(self) -> int:
        """Return the highest rotation order found (0 if none)."""
        if not self.proper_axes:
            return 0
        return max(ax.order for ax in self.proper_axes)

    def count_sigma(self) -> int:
        return len(self.reflection_planes)

    def has_sn(self, n: int) -> bool:
        return any(ax.order == n for ax in self.improper_axes)

    def principal_cn_axis(self) -> np.ndarray | None:
        """Return the axis vector of the highest-order Cn (None if no Cn found)."""
        if not self.proper_axes:
            return None
        best = max(self.proper_axes, key=lambda a: a.order)
        return best.axis

    # ------------------------------------------------------------------
    # 1. Inversion centre
    # ------------------------------------------------------------------

    def find_inversion_centre(self) -> None:
        """
        Test whether the molecule has an inversion centre (i).

        Chemistry meaning
        -----------------
        An inversion centre means every atom at position (x, y, z) has an
        identical atom at (-x, -y, -z).  Examples: benzene (D6h) has i,
        water (C2v) does not.

        The test is simply: apply the transformation r → -r to all coordinates
        and check whether the resulting set of positions is equivalent to the
        original.
        """
        coords    = self.molecule.coords
        elements  = self.molecule.elements
        inverted  = -coords   # inversion: (x,y,z) → (-x,-y,-z)
        self.has_inversion = are_equivalent(coords, inverted, elements)

    # ------------------------------------------------------------------
    # 2. Proper rotation axes (Cn)
    # ------------------------------------------------------------------

    def find_proper_rotational_axes(self) -> None:
        """
        Search for all proper rotation axes Cn (n = 2 … MAX_CN_ORDER).

        Chemistry meaning
        -----------------
        A Cn axis means the molecule looks identical after rotating by 360°/n.
        C2 in water: rotate 180° about the bisector of the H-O-H angle.
        C6 in benzene: rotate 60° about the axis perpendicular to the ring.

        Search strategy (mirroring the C++ source)
        -------------------------------------------
        1. Generate candidate axis directions (see _generate_candidate_axes).
        2. For each candidate, skip it if axis_inertially_allowed returns False
           for that (axis, n) combination — this prunes physically impossible
           choices without running the full equivalence check.
        3. For each surviving (axis, n) pair, build the Cn rotation matrix and
           call are_equivalent.  If it passes, record the axis.
        4. Deduplicate: do not add an axis that is parallel to an already-found
           axis of the same order.
        """
        candidates = self._generate_candidate_axes()
        coords     = self.molecule.coords
        elements   = self.molecule.elements

        for axis in candidates:
            for n in range(2, MAX_CN_ORDER + 1):
                if not self.axis_inertially_allowed(axis, n):
                    continue

                angle  = 2.0 * np.pi / n
                R      = rotation_matrix(axis, angle)
                rotated = apply_matrix(coords, R)

                if are_equivalent(coords, rotated, elements):
                    # Only store if we don't already have a parallel axis of this order
                    if not self._have_axis(axis, n):
                        self.proper_axes.append(RotationAxis(axis=axis.copy(), order=n))

    # ------------------------------------------------------------------
    # 3. Mirror planes (σ)
    # ------------------------------------------------------------------

    def find_reflection_planes(self) -> None:
        """
        Search for all mirror planes σ.

        Chemistry meaning
        -----------------
        A mirror plane maps the molecule onto its reflection.  σh ('horizontal')
        is perpendicular to the principal rotation axis.  σv ('vertical') contains
        the principal axis.  σd ('dihedral') bisects the angle between adjacent
        σv planes.  The labelling (h/v/d) is done later in point_group.py;
        here we just find the planes.

        Each plane is defined by its unit normal vector.  We test the same
        candidate directions used for rotation axes, plus two additional sets:

        a) Cross-products of pairs of found Cn axes — catch planes whose
           normals are not along any atom direction (e.g. σh in D6h).
        b) Cross-products of each found Cn axis with each atom direction —
           this generates the σv / σd normals for groups like C3v, where the
           plane normal is perpendicular to BOTH the Cn axis AND the atom
           vector (e.g. the three σv normals in ammonia are
           cross(C3, N−H_direction) for each of the three N−H bonds).
        """
        candidates = self._generate_candidate_axes()

        coords   = self.molecule.coords
        elements = self.molecule.elements

        axes_vecs = [ax.axis for ax in self.proper_axes]

        # (a) Cross-products of Cn axis pairs
        for i in range(len(axes_vecs)):
            for j in range(i + 1, len(axes_vecs)):
                cross = np.cross(axes_vecs[i], axes_vecs[j])
                norm  = np.linalg.norm(cross)
                if norm > GEOMETRY_TOLERANCE:
                    candidates.append(cross / norm)

        # (b) Cross-products of each Cn axis with each atom position vector.
        #     For C3v (e.g. ammonia): cross(C3, H_dir) points along the σv normal.
        #     For C4v / C6v: cross(Cn, atom_dir) gives σv and σd normals.
        for cn_vec in axes_vecs:
            for pos in coords:
                pnorm = np.linalg.norm(pos)
                if pnorm > GEOMETRY_TOLERANCE:
                    cross = np.cross(cn_vec, pos / pnorm)
                    cnorm = np.linalg.norm(cross)
                    if cnorm > GEOMETRY_TOLERANCE:
                        candidates.append(cross / cnorm)

        for normal in candidates:
            M = reflection_matrix(normal)
            reflected = apply_matrix(coords, M)

            if are_equivalent(coords, reflected, elements):
                if not self._have_plane(normal):
                    self.reflection_planes.append(ReflectionPlane(normal=normal.copy()))

    # ------------------------------------------------------------------
    # 4. Improper rotation axes (Sn)
    # ------------------------------------------------------------------

    def find_improper_rotational_axes(self) -> None:
        """
        Search for improper rotation axes Sn.

        Chemistry meaning
        -----------------
        The Sn operation is: rotate by 360°/n around the axis, then reflect
        through the plane perpendicular to the axis.  Despite the two-step
        definition, Sn is a single symmetry operation.

        Key examples:
        - S2  = inversion centre (already found separately)
        - S4  in allene (D2d): the molecule has no C4, but rotating by 90°
          then reflecting gives back the same structure
        - S6  in staggered ethane (D3d): rotate 60° then reflect
        - S8  in octasulfur (D4d): rotate 45° then reflect

        Search strategy (same as C++ source)
        -------------------------------------
        For each found Cn axis, test both Sn (same order) and S2n (double order).
        This is sufficient because in practice all Sn axes are collinear with
        some Cn axis.
        """
        coords   = self.molecule.coords
        elements = self.molecule.elements
        tested   = set()   # (axis_tuple, n) pairs already tested

        for cn_axis in self.proper_axes:
            axis = cn_axis.axis
            axis_key = tuple(axis.round(4))

            for n in [cn_axis.order, 2 * cn_axis.order]:
                if n < 3:
                    continue   # S1=σ and S2=i are handled elsewhere

                key = (axis_key, n)
                if key in tested:
                    continue
                tested.add(key)

                # Sn matrix: rotate by 2π/n then reflect through ⊥ plane
                R = rotation_matrix(axis, 2.0 * np.pi / n)
                M = reflection_matrix(axis)          # plane ⊥ to axis
                Sn_mat = M @ R                       # reflect after rotate

                transformed = apply_matrix(coords, Sn_mat)

                if are_equivalent(coords, transformed, elements):
                    if not any(
                        ax.order == n and axes_are_parallel(ax.axis, axis, AXIS_PARALLEL_TOL)
                        for ax in self.improper_axes
                    ):
                        self.improper_axes.append(ImproperAxis(axis=axis.copy(), order=n))

        # Also test Sn along each principal axis independently
        # (catches cases like S4 in Td where the C2 axis is a principal axis)
        for i in range(3):
            pax = self.molecule.principal_axes[:, i]
            pax_key = tuple(pax.round(4))
            for n in range(3, 2 * MAX_CN_ORDER + 1):
                key = (pax_key, n)
                if key in tested:
                    continue
                tested.add(key)

                R = rotation_matrix(pax, 2.0 * np.pi / n)
                M = reflection_matrix(pax)
                Sn_mat = M @ R
                transformed = apply_matrix(coords, Sn_mat)

                if are_equivalent(coords, transformed, elements):
                    if not any(
                        ax.order == n and axes_are_parallel(ax.axis, pax, AXIS_PARALLEL_TOL)
                        for ax in self.improper_axes
                    ):
                        self.improper_axes.append(ImproperAxis(axis=pax.copy(), order=n))

    # ------------------------------------------------------------------
    # Axis allowance filter  (mirrors C++ axisInertiallyAllowed)
    # ------------------------------------------------------------------

    def axis_inertially_allowed(self, axis: np.ndarray, n: int) -> bool:
        """
        Return True if a Cn axis of order n is geometrically consistent with
        the molecule's rotor class.

        Chemistry meaning
        -----------------
        The rotor class (from the principal moments of inertia) tells us what
        symmetry is even possible.  For example, a water molecule (asymmetric
        top) cannot have a C5 axis — there is no physical way to arrange 3
        atoms (of two different elements) with 5-fold symmetry.  By filtering
        out impossible axes before the expensive equivalence check, the search
        runs much faster.

        Rules (matching the C++ source)
        --------------------------------
        Linear        : only the molecular axis is tested (for C∞v / D∞h)
        Spherical top : any candidate axis is allowed (Td, Oh, Ih need many axes)
        n = 2         : C2 axes are always allowed regardless of rotor class
        Symmetric top : for n > 2, only axes close to the unique symmetry axis
        Asymmetric top: for n > 2, only axes close to one of the 3 principal axes

        Parameters
        ----------
        axis : np.ndarray (3,) — candidate rotation axis (unit vector)
        n    : int              — rotation order being tested

        Returns
        -------
        bool
        """
        rotor = self.molecule.rotor_type

        if rotor == ROTOR_LINEAR:
            # The molecular axis corresponds to the smallest principal moment.
            # Only test along it; perpendicular axes carry no useful information
            # for linear molecules.
            mol_axis = self.molecule.principal_axes[:, 0]
            return axes_are_parallel(axis, mol_axis, AXIS_PARALLEL_TOL)

        if rotor == ROTOR_SPHERICAL_TOP:
            # All axes are candidates — Td, Oh, Ih have many non-trivial ones
            return True

        if n == 2:
            # C2 is always worth testing regardless of rotor type
            return True

        # For n > 2 and non-spherical rotors: only allow axes close to the
        # unique symmetry axis (or a principal axis for asymmetric tops)
        unique = self._unique_axis()

        if unique is not None:
            # Prolate or oblate symmetric top: higher-order Cn must be along
            # the unique axis (the one with the non-degenerate moment)
            return axes_are_parallel(axis, unique, AXIS_PARALLEL_TOL)

        # Asymmetric top: higher-order Cn (rare but possible) only along
        # the three principal axes
        for i in range(3):
            if axes_are_parallel(axis, self.molecule.principal_axes[:, i], AXIS_PARALLEL_TOL):
                return True
        return False

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _unique_axis(self) -> np.ndarray | None:
        """
        Return the unique symmetry axis for symmetric tops, or None.

        Prolate top (Ia < Ib ≈ Ic): unique axis = principal_axes[:,0]
            — the 'long' axis with the smallest moment of inertia.
        Oblate top (Ia ≈ Ib < Ic): unique axis = principal_axes[:,2]
            — the axis perpendicular to the flat face, with the largest moment.
        """
        rotor = self.molecule.rotor_type
        if rotor == ROTOR_PROLATE_SYMMETRIC:
            return self.molecule.principal_axes[:, 0]
        if rotor == ROTOR_OBLATE_SYMMETRIC:
            return self.molecule.principal_axes[:, 2]
        return None

    def _generate_candidate_axes(self) -> list[np.ndarray]:
        """
        Build the list of candidate axis directions to test.

        Sources (matching the C++ search strategy):
        1. Bond-graph ring centroids for large spherical tops (FIRST, so they
           survive deduplication — pair-midpoint approximations are dropped
           in their favour, not the other way around).
        2. The three principal axes of the inertia tensor.
        3. Vectors from the origin through each atom's position.
        4. Vectors from the origin through the midpoint of each pair of
           same-element atoms.
        5. Triple centroids for small same-element groups in spherical tops
           (C(6,3)=20 for SF6; covers triangular face axes like (1,1,1)/√3).

        All directions are normalised to unit vectors.  Near-duplicate
        directions (parallel within AXIS_PARALLEL_TOL) are removed.

        Returns
        -------
        list of np.ndarray, each shape (3,), unit length
        """
        candidates: list[np.ndarray] = []
        coords   = self.molecule.coords
        elements = self.molecule.elements
        N = len(elements)

        same_elem: dict[str, list[int]] = {}
        for idx, elem in enumerate(elements):
            same_elem.setdefault(elem, []).append(idx)

        # 1. Bond-graph ring centroids for large spherical-top molecules.
        #
        #    Chemistry: Ih molecules (e.g. C60) have C5 axes through the centres
        #    of pentagonal faces and C3 axes through hexagonal faces.  These
        #    exact directions are NOT along any atom position or pair midpoint.
        #    Finding all 5-cycles and 6-cycles in the bond graph and using their
        #    centroids gives the correct axis directions.
        #
        #    Ordering matters: ring centroids are inserted FIRST so that any
        #    nearby pair-midpoint approximation (which might differ by ~3°) is
        #    dropped during deduplication rather than the exact ring centroid.
        if (self.molecule.rotor_type == ROTOR_SPHERICAL_TOP
                and any(len(idxs) > 20 for idxs in same_elem.values())):

            # Bond adjacency: atom pair bonded if distance < 1.5 × shortest bond
            dist_sq = np.sum((coords[:, None] - coords[None, :]) ** 2, axis=2)
            np.fill_diagonal(dist_sq, np.inf)
            min_dist_sq = dist_sq.min()
            thresh_sq = (1.5 ** 2) * min_dist_sq
            adj: list[list[int]] = [
                list(np.where(dist_sq[i] < thresh_sq)[0]) for i in range(N)
            ]

            # Find all 5-cycles (pentagons) and 6-cycles (hexagons) and add
            # their centroids as candidate axis directions.
            for ring_size in (5, 6):
                seen_rings: set[tuple[int, ...]] = set()
                for a in range(N):
                    for b in adj[a]:
                        for c in adj[b]:
                            if c == a:
                                continue
                            if ring_size == 5:
                                for d in adj[c]:
                                    if d in (a, b):
                                        continue
                                    for e in adj[d]:
                                        if e in (a, b, c):
                                            continue
                                        if a in adj[e]:
                                            key = tuple(sorted((a, b, c, d, e)))
                                            if key not in seen_rings:
                                                seen_rings.add(key)
                                                cen = coords[list(key)].mean(axis=0)
                                                nn = np.linalg.norm(cen)
                                                if nn > GEOMETRY_TOLERANCE:
                                                    candidates.append(cen / nn)
                            else:  # ring_size == 6
                                for d in adj[c]:
                                    if d in (a, b):
                                        continue
                                    for e in adj[d]:
                                        if e in (a, b, c):
                                            continue
                                        for f in adj[e]:
                                            if f in (a, b, c, d):
                                                continue
                                            if a in adj[f]:
                                                key = tuple(sorted((a, b, c, d, e, f)))
                                                if key not in seen_rings:
                                                    seen_rings.add(key)
                                                    cen = coords[list(key)].mean(axis=0)
                                                    nn = np.linalg.norm(cen)
                                                    if nn > GEOMETRY_TOLERANCE:
                                                        candidates.append(cen / nn)

        # 2. Principal axes
        for i in range(3):
            candidates.append(self.molecule.principal_axes[:, i].copy())

        # 3. Through each atom (skip atoms very close to the origin)
        for pos in coords:
            norm = np.linalg.norm(pos)
            if norm > GEOMETRY_TOLERANCE:
                candidates.append(pos / norm)

        # 4. Midpoints of same-element pairs
        for i in range(N):
            for j in range(i + 1, N):
                if elements[i] == elements[j]:
                    mid = coords[i] + coords[j]
                    norm = np.linalg.norm(mid)
                    if norm > GEOMETRY_TOLERANCE:
                        candidates.append(mid / norm)

        # 5. Face-centre directions from triple centroids for small groups.
        #
        #    Chemistry: Oh molecules (SF6, cubane) have C3 axes along (1,1,1)/√3
        #    — the centres of octahedral triangular faces.  These are not along
        #    any atom direction or pair midpoint, but they ARE the centroid of
        #    a triple of same-element atoms.  C(6,3)=20 for SF6; manageable.
        if self.molecule.rotor_type == ROTOR_SPHERICAL_TOP:
            from itertools import combinations
            for idxs in same_elem.values():
                if len(idxs) <= 20:
                    for triple in combinations(idxs, 3):
                        centroid = coords[list(triple)].mean(axis=0)
                        norm = np.linalg.norm(centroid)
                        if norm > GEOMETRY_TOLERANCE:
                            candidates.append(centroid / norm)

        # Deduplicate: keep only one representative per parallel direction
        unique: list[np.ndarray] = []
        for ax in candidates:
            if not any(axes_are_parallel(ax, u, AXIS_PARALLEL_TOL) for u in unique):
                unique.append(ax)

        return unique

    def _have_axis(self, axis: np.ndarray, n: int) -> bool:
        """Return True if a Cn of order n parallel to `axis` is already stored."""
        return any(
            ax.order == n and axes_are_parallel(ax.axis, axis, AXIS_PARALLEL_TOL)
            for ax in self.proper_axes
        )

    def _have_plane(self, normal: np.ndarray) -> bool:
        """Return True if a mirror plane with this normal is already stored."""
        return any(
            axes_are_parallel(pl.normal, normal, AXIS_PARALLEL_TOL)
            for pl in self.reflection_planes
        )

    # ------------------------------------------------------------------
    # String representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        cn_summary = {}
        for ax in self.proper_axes:
            cn_summary[ax.order] = cn_summary.get(ax.order, 0) + 1
        sn_summary = {}
        for ax in self.improper_axes:
            sn_summary[ax.order] = sn_summary.get(ax.order, 0) + 1

        parts = []
        for n in sorted(cn_summary):
            parts.append(f"C{n}×{cn_summary[n]}")
        if self.has_inversion:
            parts.append("i")
        if self.reflection_planes:
            parts.append(f"σ×{len(self.reflection_planes)}")
        for n in sorted(sn_summary):
            parts.append(f"S{n}×{sn_summary[n]}")

        return f"SymmetryFinder({', '.join(parts) or 'E only'})"
