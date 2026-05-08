"""
point_group.py — PointGroupClassifier class

Given the symmetry elements found by SymmetryFinder, this module:
  1. Matches them against a library of known point groups to identify the
     best-fit Schoenflies symbol (C2v, D6h, Td, Oh, …).
  2. Assigns the standard Cartesian axes (z = principal rotation axis).
  3. Labels each mirror plane as σh, σv, or σd and each C2 as C2' or C2''.

This is the final stage of the Schoenflies algorithm.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field

from .utils import GEOMETRY_TOLERANCE, axes_are_parallel
from .molecule import (
    Molecule,
    ROTOR_LINEAR,
    ROTOR_SPHERICAL_TOP,
    ROTOR_PROLATE_SYMMETRIC,
    ROTOR_OBLATE_SYMMETRIC,
    ROTOR_ASYMMETRIC,
)
from .symmetry_elements import SymmetryFinder, RotationAxis, ReflectionPlane

AXIS_TOL = 0.1   # radians — same as AXIS_PARALLEL_TOL in symmetry_elements


# ---------------------------------------------------------------------------
# Point group library record
# ---------------------------------------------------------------------------

@dataclass
class PGRecord:
    """
    Describes the required symmetry content of one Schoenflies point group.

    Fields
    ------
    name   : Schoenflies symbol, e.g. 'C2v', 'D6h', 'Td'
    cn     : dict mapping rotation order n → required count of Cn axes
    inv    : True if an inversion centre is required
    sigma  : required number of mirror planes
    sn     : list of Sn orders that must be present (at least one axis each)
    """
    name:  str
    cn:    dict[int, int]
    inv:   bool
    sigma: int
    sn:    list[int]


# ---------------------------------------------------------------------------
# Point group library  (mirrors the C++ point_groups.cpp table)
# ---------------------------------------------------------------------------
# Each entry gives the EXACT expected count of each symmetry element.
# The scorer picks the entry where:
#   (a) all required elements are present (found >= required), AND
#   (b) the total excess (sum of found − required over all elements) is minimal.
#
# Convention for Cn counts: a C4 axis also contributes to the C2 count
# (because C4² = C2).  These overlapping counts are included explicitly so
# the library matches what SymmetryFinder actually reports.
#
# Linear groups (C∞v, D∞h) are handled separately before library lookup,
# because their infinite-order axes cannot be enumerated numerically.

POINT_GROUP_LIBRARY: list[PGRecord] = [

    # ── Non-axial ────────────────────────────────────────────────────────
    PGRecord('C1',  cn={},                      inv=False, sigma=0,  sn=[]),
    PGRecord('Ci',  cn={},                      inv=True,  sigma=0,  sn=[]),
    PGRecord('Cs',  cn={},                      inv=False, sigma=1,  sn=[]),

    # ── Cyclic Cn  (rotation axis only, no mirrors) ──────────────────────
    # Note: Cn group contains C_n, C_n^2, …  The C2 subelement of C4
    # appears explicitly in the count (C4² = C2).
    PGRecord('C2',  cn={2:1},                   inv=False, sigma=0,  sn=[]),
    PGRecord('C3',  cn={3:1},                   inv=False, sigma=0,  sn=[]),
    PGRecord('C4',  cn={4:1, 2:1},              inv=False, sigma=0,  sn=[]),
    PGRecord('C5',  cn={5:1},                   inv=False, sigma=0,  sn=[]),
    PGRecord('C6',  cn={6:1, 3:1, 2:1},         inv=False, sigma=0,  sn=[]),
    PGRecord('C7',  cn={7:1},                   inv=False, sigma=0,  sn=[]),
    PGRecord('C8',  cn={8:1, 4:1, 2:1},         inv=False, sigma=0,  sn=[]),

    # ── Cnh  (Cn + horizontal mirror) ───────────────────────────────────
    PGRecord('C2h', cn={2:1},                   inv=True,  sigma=1,  sn=[]),
    PGRecord('C3h', cn={3:1},                   inv=False, sigma=1,  sn=[3]),
    PGRecord('C4h', cn={4:1, 2:1},              inv=True,  sigma=1,  sn=[4]),
    PGRecord('C5h', cn={5:1},                   inv=False, sigma=1,  sn=[5]),
    PGRecord('C6h', cn={6:1, 3:1, 2:1},         inv=True,  sigma=1,  sn=[3, 6]),

    # ── Cnv  (Cn + vertical mirrors) ─────────────────────────────────────
    PGRecord('C2v', cn={2:1},                   inv=False, sigma=2,  sn=[]),
    PGRecord('C3v', cn={3:1},                   inv=False, sigma=3,  sn=[]),
    PGRecord('C4v', cn={4:1, 2:1},              inv=False, sigma=4,  sn=[]),
    PGRecord('C5v', cn={5:1},                   inv=False, sigma=5,  sn=[]),
    PGRecord('C6v', cn={6:1, 3:1, 2:1},         inv=False, sigma=6,  sn=[]),
    PGRecord('C7v', cn={7:1},                   inv=False, sigma=7,  sn=[]),
    PGRecord('C8v', cn={8:1, 4:1, 2:1},         inv=False, sigma=8,  sn=[]),

    # ── Dihedral Dn  (Cn + n perpendicular C2, no mirrors) ───────────────
    # D_n has 1 principal Cn + n perpendicular C2 axes.
    # The C2 count includes the C2 from the principal axis (e.g. C4² = C2)
    # plus the n perpendicular C2.
    PGRecord('D2',  cn={2:3},                   inv=False, sigma=0,  sn=[]),
    PGRecord('D3',  cn={3:1, 2:3},              inv=False, sigma=0,  sn=[]),
    PGRecord('D4',  cn={4:1, 2:5},              inv=False, sigma=0,  sn=[]),
    PGRecord('D5',  cn={5:1, 2:5},              inv=False, sigma=0,  sn=[]),
    PGRecord('D6',  cn={6:1, 3:1, 2:7},         inv=False, sigma=0,  sn=[]),
    PGRecord('D7',  cn={7:1, 2:7},              inv=False, sigma=0,  sn=[]),

    # ── Dnh  (Dn + horizontal mirror) ────────────────────────────────────
    # σh count = 1 σh + n σv.  Total planes = n + 1.
    PGRecord('D2h', cn={2:3},                   inv=True,  sigma=3,  sn=[]),
    PGRecord('D3h', cn={3:1, 2:3},              inv=False, sigma=4,  sn=[3]),
    PGRecord('D4h', cn={4:1, 2:5},              inv=True,  sigma=5,  sn=[4]),
    PGRecord('D5h', cn={5:1, 2:5},              inv=False, sigma=6,  sn=[5]),
    PGRecord('D6h', cn={6:1, 3:1, 2:7},         inv=True,  sigma=7,  sn=[3, 6]),
    PGRecord('D7h', cn={7:1, 2:7},              inv=False, sigma=8,  sn=[7]),
    PGRecord('D8h', cn={8:1, 4:1, 2:9},         inv=True,  sigma=9,  sn=[4, 8]),

    # ── Dnd  (Dn + dihedral mirrors) ─────────────────────────────────────
    # σd count = n.  Principal Sn order = 2n.
    PGRecord('D2d', cn={2:3},                   inv=False, sigma=2,  sn=[4]),
    PGRecord('D3d', cn={3:1, 2:3},              inv=True,  sigma=3,  sn=[6]),
    PGRecord('D4d', cn={4:1, 2:5},              inv=False, sigma=4,  sn=[8]),
    PGRecord('D5d', cn={5:1, 2:5},              inv=True,  sigma=5,  sn=[10]),
    PGRecord('D6d', cn={6:1, 3:1, 2:7},         inv=False, sigma=6,  sn=[12]),

    # ── Cubic groups ─────────────────────────────────────────────────────
    # T (chiral tetrahedral — very rare in practice)
    PGRecord('T',   cn={3:4, 2:3},              inv=False, sigma=0,  sn=[]),
    # Th (pyritohedral)
    PGRecord('Th',  cn={3:4, 2:3},              inv=True,  sigma=3,  sn=[6]),
    # Td (tetrahedral — CH4, CCl4, P4, etc.)
    PGRecord('Td',  cn={3:4, 2:3},              inv=False, sigma=6,  sn=[4]),
    # O (chiral octahedral — rare)
    PGRecord('O',   cn={4:3, 3:4, 2:9},         inv=False, sigma=0,  sn=[]),
    # Oh (octahedral — SF6, cubane, etc.)
    PGRecord('Oh',  cn={4:3, 3:4, 2:9},         inv=True,  sigma=9,  sn=[4, 6]),
    # I (chiral icosahedral — rare)
    PGRecord('I',   cn={5:6, 3:10, 2:15},       inv=False, sigma=0,  sn=[]),
    # Ih (full icosahedral — C60, B12H12²⁻, etc.)
    PGRecord('Ih',  cn={5:6, 3:10, 2:15},       inv=True,  sigma=15, sn=[10]),
]


# ---------------------------------------------------------------------------
# PointGroupClassifier
# ---------------------------------------------------------------------------

class PointGroupClassifier:
    """
    Determines the Schoenflies point group of a molecule from its found
    symmetry elements, then assigns standard Cartesian axes and labels
    each operation.

    Usage
    -----
        mol = Molecule('benzene.xyz')
        sf  = SymmetryFinder(mol)
        sf.find_all()
        pgc = PointGroupClassifier(mol, sf)
        pgc.classify()
        print(pgc.symbol)          # 'D6h'
        print(pgc.z_axis)          # array([0., 0., 1.])  (principal C6 axis)
    """

    def __init__(self, molecule: Molecule, finder: SymmetryFinder) -> None:
        self.molecule = molecule
        self.finder   = finder

        # Results — set by classify()
        self.symbol:   str          = 'C1'
        self.z_axis:   np.ndarray   = np.array([0., 0., 1.])
        self.x_axis:   np.ndarray   = np.array([1., 0., 0.])
        self.sigma_labels: dict[int, str] = {}   # index → 'h'/'v'/'d'
        self.cn_labels:    dict[int, str] = {}   # index → "C2'"/"C2''" etc.

    def classify(self) -> str:
        """
        Run the full classification pipeline and return the Schoenflies symbol.

        Pipeline (matches C++ source)
        ------------------------------
        1. Special-case linear molecules (C∞v / D∞h).
        2. Score all library entries and pick the best match.
        3. Assign Cartesian axes (z = principal Cn, x = chosen C2 or σ normal).
        4. Label mirror planes (σh / σv / σd) and C2 axes (C2' / C2'').
        """
        sf = self.finder

        # Step 1 — linear molecules cannot be matched via the finite library
        if self.molecule.rotor_type == ROTOR_LINEAR:
            self.symbol = 'D_inf_h' if sf.has_inversion else 'C_inf_v'
            self.z_axis = self.molecule.principal_axes[:, 0]
            return self.symbol

        # Step 2 — library matching
        self.symbol = self._find_best_match()

        # Step 3 — assign Cartesian axes
        self._find_cartesian_axes()

        # Step 4 — label operations
        self._label_operations()

        return self.symbol

    # ------------------------------------------------------------------
    # Scoring and match selection
    # ------------------------------------------------------------------

    def _score(self, pg: PGRecord) -> int:
        """
        Compute the match score between the found elements and a library entry.

        Chemistry meaning
        -----------------
        A perfect match (found == required for every element type) scores 0.
        Each extra found element beyond the requirement adds +1.  If any
        required element is MISSING (found < required), the group is
        disqualified and we return a large sentinel value.

        Algorithm
        ---------
        excess = 0
        for each element type e:
            if found(e) < required(e):  return DISQUALIFIED   (-∞ in practice)
            excess += found(e) - required(e)
        return excess

        Parameters
        ----------
        pg : PGRecord — one row from the library

        Returns
        -------
        int : 0 = perfect match, >0 = extra elements found, -1 = disqualified
        """
        DISQUALIFIED = -1
        sf = self.finder

        # Check all required Cn axes
        for n, req_count in pg.cn.items():
            if sf.count_cn(n) < req_count:
                return DISQUALIFIED

        # Check inversion centre
        if pg.inv and not sf.has_inversion:
            return DISQUALIFIED

        # Check mirror planes
        if sf.count_sigma() < pg.sigma:
            return DISQUALIFIED

        # Check required Sn axes
        for n in pg.sn:
            if not sf.has_sn(n):
                return DISQUALIFIED

        # All required elements present — compute total excess
        excess = 0

        # Excess Cn (for orders 2..MAX_CN_ORDER)
        for n in range(2, 9):
            excess += max(0, sf.count_cn(n) - pg.cn.get(n, 0))

        # Excess mirror planes
        excess += sf.count_sigma() - pg.sigma

        # Excess inversion (unusual but possible if the library entry has inv=False)
        if sf.has_inversion and not pg.inv:
            excess += 1

        # Excess Sn (any found order not listed as required)
        # We count each unique Sn order found but not listed in pg.sn
        for ax in sf.improper_axes:
            if ax.order not in pg.sn:
                excess += 1

        return excess

    def _find_best_match(self) -> str:
        """
        Score all library entries and return the name of the best match.

        The best match is the qualified entry (score ≥ 0) with the lowest
        score.  Ties are broken by choosing the entry with the larger total
        required element count — i.e. the more specific (higher-symmetry)
        group — to avoid trivially classifying everything as C1.

        Returns
        -------
        str : Schoenflies symbol of the best match
        """
        best_name  = 'C1'
        best_score = 10**9
        best_size  = -1   # total required element count for tie-breaking

        for pg in POINT_GROUP_LIBRARY:
            s = self._score(pg)
            if s < 0:
                continue   # disqualified

            size = sum(pg.cn.values()) + pg.sigma + (1 if pg.inv else 0) + len(pg.sn)

            if s < best_score or (s == best_score and size > best_size):
                best_score = s
                best_name  = pg.name
                best_size  = size

        return best_name

    # ------------------------------------------------------------------
    # Cartesian axis assignment
    # ------------------------------------------------------------------

    def _find_cartesian_axes(self) -> None:
        """
        Set self.z_axis (principal rotation axis) and self.x_axis.

        Chemistry meaning
        -----------------
        By convention:
        - z  = the principal rotation axis (highest-order Cn).
          If no Cn is found (C1, Ci, Cs), z defaults to the principal
          inertia axis or the mirror plane normal.
        - x  = chosen so that the xz plane contains the most atoms, or
          passes through a C2 axis perpendicular to z, or is a σv normal.

        This matches the C++ find_cartesian_axes logic.
        """
        sf  = self.finder
        mol = self.molecule

        # z-axis: highest-order Cn
        if sf.proper_axes:
            best = max(sf.proper_axes, key=lambda a: a.order)
            self.z_axis = best.axis.copy()
        elif sf.reflection_planes:
            # Cs: z perpendicular to the mirror plane
            self.z_axis = sf.reflection_planes[0].normal.copy()
        else:
            # C1 or Ci: use the principal inertia axis
            self.z_axis = mol.principal_axes[:, 2].copy()

        # x-axis: choose a direction perpendicular to z that passes
        # through the most atoms, or falls along a C2 or σ normal.
        self.x_axis = self._choose_x_axis()

    def _choose_x_axis(self) -> np.ndarray:
        """
        Pick the x-axis as the perpendicular direction through the most atoms.

        We project each atom position onto the plane perpendicular to z and
        find the direction in that plane that has the most atoms lying on it
        (within GEOMETRY_TOLERANCE of the projection).  If no atoms project
        onto distinct directions, fall back to a Gram-Schmidt perpendicular.
        """
        z = self.z_axis
        coords = self.molecule.coords

        # Project atom positions onto the plane perpendicular to z
        projections = []
        for pos in coords:
            p = pos - np.dot(pos, z) * z
            n = np.linalg.norm(p)
            if n > GEOMETRY_TOLERANCE:
                projections.append(p / n)

        if not projections:
            return _gram_schmidt_perp(z)

        # Count how many projections each direction aligns with
        best_dir   = projections[0]
        best_count = 0
        for candidate in projections:
            count = sum(
                1 for p in projections
                if axes_are_parallel(candidate, p, AXIS_TOL)
            )
            if count > best_count:
                best_count = count
                best_dir   = candidate

        return best_dir

    # ------------------------------------------------------------------
    # Operation labelling
    # ------------------------------------------------------------------

    def _label_operations(self) -> None:
        """
        Label each mirror plane as σh, σv, or σd and each perpendicular
        C2 as C2' or C2''.

        Chemistry meaning
        -----------------
        σh ('horizontal'): perpendicular to the principal axis (z).
            Its normal is parallel to z.
        σv ('vertical'):   contains the principal axis.
            Its normal is perpendicular to z.
        σd ('dihedral'):   also contains the principal axis, but bisects
            the angle between adjacent C2' axes.
            Distinguished from σv by checking whether any C2 axis lies
            IN the plane (C2 axis ⊥ plane normal).

        C2':  perpendicular C2 that passes through atoms (or bonds).
        C2'': perpendicular C2 that bisects the angle between C2' axes.

        Results are stored in self.sigma_labels and self.cn_labels.
        """
        sf = self.finder
        z  = self.z_axis

        # ---- Label mirror planes ----------------------------------------
        self.sigma_labels = {}
        for idx, plane in enumerate(sf.reflection_planes):
            n = plane.normal

            if axes_are_parallel(n, z, AXIS_TOL):
                # Normal parallel to z → plane is perpendicular to z → σh
                label = 'h'
            else:
                # Normal perpendicular to z → plane contains z → σv or σd
                # σd bisects C2' axes: check whether any C2 axis lies in the
                # plane (C2 axis ⊥ plane normal, AND C2 axis ⊥ z)
                in_plane_c2 = any(
                    ax.order == 2
                    and not axes_are_parallel(ax.axis, z, AXIS_TOL)
                    and abs(np.dot(ax.axis, n)) < AXIS_TOL
                    for ax in sf.proper_axes
                )
                label = 'v' if in_plane_c2 else 'd'

            self.sigma_labels[idx] = label

        # ---- Label C2 axes -----------------------------------------------
        self.cn_labels = {}
        # Collect C2 axes perpendicular to z
        perp_c2 = [
            (idx, ax)
            for idx, ax in enumerate(sf.proper_axes)
            if ax.order == 2 and not axes_are_parallel(ax.axis, z, AXIS_TOL)
        ]

        # A C2 is C2' if it passes through σv planes (lies in a σv plane);
        # otherwise C2''.
        sigma_v_normals = [
            sf.reflection_planes[i].normal
            for i, lbl in self.sigma_labels.items()
            if lbl == 'v'
        ]

        for idx, ax in perp_c2:
            # C2 lies IN a σv plane if C2 axis ⊥ σv normal
            in_sigma_v = any(
                abs(np.dot(ax.axis, sv_n)) < AXIS_TOL
                for sv_n in sigma_v_normals
            )
            self.cn_labels[idx] = "C2'" if in_sigma_v else "C2''"

    # ------------------------------------------------------------------
    # String representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"PointGroupClassifier(symbol='{self.symbol}')"


# ---------------------------------------------------------------------------
# Helper — Gram-Schmidt perpendicular
# ---------------------------------------------------------------------------

def _gram_schmidt_perp(v: np.ndarray) -> np.ndarray:
    """Return a unit vector perpendicular to v, chosen arbitrarily."""
    v = v / np.linalg.norm(v)
    # Pick the Cartesian axis least aligned with v
    idx = np.argmin(np.abs(v))
    e   = np.zeros(3); e[idx] = 1.0
    perp = e - np.dot(e, v) * v
    return perp / np.linalg.norm(perp)
