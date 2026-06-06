"""Algorithmic assignment of basis functions to irreps for axial point groups.

What are basis functions?
-------------------------
In group theory, every physical quantity (an atomic orbital, a molecular
vibration, an electric field component) transforms under symmetry operations
according to one of the group's irreducible representations.  Knowing *which*
irrep a function belongs to is essential for:
- Predicting IR/Raman activity (active only if it transforms as x, y, z or
  quadratic functions in appropriate symmetry)
- Constructing symmetry-adapted linear combinations of atomic orbitals (SALC)
- Applying selection rules in electronic spectroscopy

This module assigns the 12 standard Cartesian basis functions to irreps:
    linear: x, y, z, Rx, Ry, Rz
    quadratic: x², y², z², xy, xz, yz  (equivalently z², x²+y², x²-y², xy, xz, yz)

How it works — the reduction formula
--------------------------------------
To find which irreps a function Γ belongs to, use the *reduction formula*:

    n_i = (1/|G|) Σ_{classes}  N_c · χ_Γ(c) · χ_i(c)

where:
    |G|   = order of the group (total number of operations)
    N_c   = number of operations in conjugacy class c
    χ_Γ(c) = character of the function under class c (computed analytically below)
    χ_i(c) = character of irrep i under class c (from the character table)
    n_i   = how many times irrep i appears in Γ (must be a non-negative integer)

Standard orientation: z = principal axis, (x,y) in the equatorial plane.
Only valid for axial groups (Cn, Cnh, Cnv, Sn, Dn, Dnh, Dnd).
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING

from ..operations.operation_label import OperationLabel as OL

if TYPE_CHECKING:
    from .point_group import PointGroup


# ---------------------------------------------------------------------------
# Characters of basis function sets under a single symmetry operation
# ---------------------------------------------------------------------------

def _chi_basis_for_op(op_type: str, theta: float) -> dict[str, float]:
    """Return χ for each basis function set under one symmetry operation.

    The characters are the *traces* of the transformation matrices acting on
    each basis function set.  The key results used here are:

    Rotation by θ about z (Cn^k, θ = 2πk/n):
      - z is unchanged: χ = 1
      - (x, y) span a 2D space; the rotation matrix has trace 2cos(θ) = c1
      - (x²−y², xy) also span a 2D space but the angle effectively doubles:
        trace = 2cos(2θ) = c2  (the quadratic functions rotate twice as fast)
      - (xz, yz) also 2D with trace 2cos(θ) = c1
      - z², x²+y² are each 1D symmetric under any rotation: χ = 1

    C2 ⊥ z (C2′ or C2″, i.e. a 180° rotation about a horizontal axis):
      - z → -z: χ = -1
      - (x, y) average to 0 over the pair: χ = 0 (the rotation swaps them)
      - Rz → -Rz (pseudovector behaves oppositely to z): χ = -1
      - (Rx, Ry) → 0 similarly
      - Quadratics z², x²+y² stay: χ = 1;  cross-terms average to 0

    Inversion (i):
      - Polar vectors (x,y,z) → negated: χ = -1 each
      - Axial vectors (Rx,Ry,Rz) unchanged: χ = +1 each
      - Quadratics (even functions): all χ = +1

    Horizontal mirror σh (reflection through z=0 plane):
      - z → -z: χ = -1  (polar)
      - (x,y) unchanged: χ = 2
      - Rz unchanged: χ = +1  (axial vector ⊥ plane)
      - (Rx,Ry) → negated: χ = -2
      - Quadratics involving z (xz, yz) → sign flip: χ = -2
      - Others (z², x²+y², x²-y², xy) unchanged: χ = 1 or 2

    Vertical mirror σv or σd (reflection through a plane containing z):
      - z unchanged: χ = 1
      - (x,y) average to 0: χ = 0
      - Rz → -Rz (pseudovector): χ = -1
      - (Rx,Ry) average to 0: χ = 0
      - Quadratics: z², x²+y² unchanged; cross-terms average to 0

    Improper rotation Sn^k = Cn^k · σh:
      - Combine the Cn rotation and σh results (z gets flipped by σh).

    Parameters
    ----------
    op_type : "E", "Cn", "C2p", "C2pp", "i", "sigma_h", "sigma_v",
              "sigma_d", "Sn"
    theta   : rotation angle in radians (2π·m/d for Cn^m or Sn^m)
    """
    c1 = 2.0 * math.cos(theta)        # trace of 2D rotation matrix for (x,y)
    c2 = 2.0 * math.cos(2.0 * theta)  # trace for (x²-y², xy); angle doubles

    if op_type == "E":
        # Identity: everything is unchanged; trace = dimension of each set
        return {"z":1, "xy":2, "Rz":1, "Rxy":2,
                "z2":1, "x2y2xy":2, "xzyz":2, "x2py2":1}
    if op_type == "Cn":
        # Rotation about z by θ: z and z²,x²+y² invariant; others use c1/c2
        return {"z":1, "xy":c1, "Rz":1, "Rxy":c1,
                "z2":1, "x2y2xy":c2, "xzyz":c1, "x2py2":1}
    if op_type in ("C2p", "C2pp"):
        # 180° rotation about a horizontal axis: z→-z, (x,y) and cross-terms→0
        return {"z":-1, "xy":0, "Rz":-1, "Rxy":0,
                "z2":1, "x2y2xy":0, "xzyz":0, "x2py2":1}
    if op_type == "i":
        # Inversion: polar vectors flip, axial vectors stay, quadratics stay
        return {"z":-1, "xy":-2, "Rz":1, "Rxy":2,
                "z2":1, "x2y2xy":2, "xzyz":2, "x2py2":1}
    if op_type == "sigma_h":
        # Mirror through z=0: z→-z, (x,y) stay, Rz stays, (Rx,Ry) flip
        return {"z":-1, "xy":2, "Rz":1, "Rxy":-2,
                "z2":1, "x2y2xy":2, "xzyz":-2, "x2py2":1}
    if op_type in ("sigma_v", "sigma_d"):
        # Mirror containing z: (x,y) and cross-terms average to 0
        return {"z":1, "xy":0, "Rz":-1, "Rxy":0,
                "z2":1, "x2y2xy":0, "xzyz":0, "x2py2":1}
    if op_type == "Sn":
        # Sn^k = Cn^k · σh: start from Cn result and flip the z-parity terms
        return {"z":-1, "xy":c1, "Rz":1, "Rxy":-c1,
                "z2":1, "x2y2xy":c2, "xzyz":-c1, "x2py2":1}
    return {k: 0.0 for k in ("z","xy","Rz","Rxy","z2","x2y2xy","xzyz","x2py2")}


# ---------------------------------------------------------------------------
# Classify each column header into (op_type, theta)
# ---------------------------------------------------------------------------

def _classify_col(olc) -> tuple[str, float]:
    """Return (op_type, theta_radians) for one unique-operation column.

    Converts an OperationLabelCount column header into the (op_type, theta)
    pair that _chi_basis_for_op expects.

    The main subtlety is C2 axes in dihedral groups: a degree-2 rotation with
    a prime label (C2′ or C2″) is a *horizontal* C2 axis perpendicular to z,
    which has different characters from the principal-axis C2 (which is just
    Cn^(n/2) for even n).  The prime label distinguishes them.
    """
    lbl = olc.label
    elem = lbl.element
    E = OL.Element

    if elem == E.ProperRotation:
        d = lbl.degree
        m = lbl.multiple or 1
        theta = 2.0 * math.pi * m / d
        if d == 2:
            # A degree-2 rotation with a prime label is a perpendicular C2 axis
            # (C2′ passes through atoms/bonds; C2″ bisects them).
            pr = lbl.prime
            if pr != OL.Prime.none:
                return ("C2pp" if pr == OL.Prime.Double else "C2p"), theta
            # No prime → principal axis C2 = Cn^(n/2); treat like any Cn rotation
            return "Cn", theta
        return "Cn", theta

    if elem == E.ImproperRotation:
        d = lbl.degree
        m = lbl.multiple or 1
        theta = 2.0 * math.pi * m / d
        return "Sn", theta

    if elem == E.Inversion:
        return "i", 0.0

    if elem == E.Reflection:
        pl = lbl.plane
        if pl == OL.Plane.Horizontal:
            return "sigma_h", 0.0
        if pl == OL.Plane.Dihedral:
            return "sigma_d", 0.0
        return "sigma_v", 0.0

    return "E", 0.0


# ---------------------------------------------------------------------------
# Reduction formula
# ---------------------------------------------------------------------------

def _reduce(reducible: list[float], characters: list[list[float]],
            counts: list[int], order: int) -> list[float]:
    """Multiplicity of each irrep in a reducible representation.

    Applies the reduction formula:
        n_i = (1/|G|) Σ_c  N_c · χ_Γ(c) · χ_i(c)

    where:
        reducible[c] = χ_Γ(c)  — character of the function under class c
        characters[i][c] = χ_i(c) — character of irrep i under class c
        counts[c] = N_c         — number of operations in class c
        order = |G|             — total group order

    Returns a list of floats (one per irrep); each should be a near-integer.
    Caller uses round() to convert to integer multiplicities.
    """
    result = []
    for chi_row in characters:
        total = sum(counts[c] * reducible[c] * chi_row[c]
                    for c in range(min(len(counts), len(chi_row), len(reducible))))
        result.append(total / order)
    return result


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def compute_basis_functions(pg: PointGroup) -> dict[str, dict[str, list[str]]]:
    """Return basis function assignments for all irreps of *pg*.

    Returns
    -------
    dict  irrep_name → {"linear": [...], "quadratic": [...]}
    """
    lbl = pg.label
    # Only valid for axial groups
    if lbl.is_polyhedral() or lbl.is_linear() or lbl.group_class.name in ("C1", "Ci", "Cs"):
        return {}

    chars = pg.characters
    irreps = pg.irreps
    unique_ops = pg.unique_operations
    order = pg.order

    if not chars or order == 0:
        return {}

    # Build column metadata: one entry per character-table column (including E).
    # Each entry is (op_type, theta, count) so we can call _chi_basis_for_op
    # and weight each term by count in the reduction formula.
    col_meta: list[tuple[str, float, int]] = [("E", 0.0, 1)]  # identity always first
    for olc in unique_ops:
        op_type, theta = _classify_col(olc)
        col_meta.append((op_type, theta, olc.count))

    counts = [cm[2] for cm in col_meta]

    # For each of the 8 basis-function "sets" (z, (x,y), Rz, (Rx,Ry), z²,
    # (x²-y²,xy), (xz,yz), x²+y²), build the vector of characters under
    # every column.  This is the χ_Γ(c) vector needed by _reduce.
    keys = ("z", "xy", "Rz", "Rxy", "z2", "x2y2xy", "xzyz", "x2py2")
    sets: dict[str, list[float]] = {k: [] for k in keys}
    for op_type, theta, _ in col_meta:
        chi = _chi_basis_for_op(op_type, theta)
        for k in keys:
            sets[k].append(chi[k])

    # Apply the reduction formula to every basis-function set.
    # multiplicities[key][i] ≈ integer: how many times irrep i appears in set key.
    multiplicities = {k: _reduce(v, chars, counts, order) for k, v in sets.items()}

    result: dict[str, dict[str, list[str]]] = {
        ir.name: {"linear": [], "quadratic": []} for ir in irreps
    }

    def _assign(key: str, labels: list[str], category: str) -> None:
        # For each irrep, if it appears at least once in this basis-function set
        # (multiplicity ≥ 1 after rounding), add the display labels to that irrep's
        # entry.  round() corrects for tiny floating-point errors in the sum.
        for i, ir in enumerate(irreps):
            mults = multiplicities[key]
            if i < len(mults) and round(mults[i]) >= 1:
                result[ir.name][category].extend(labels)

    # Map each computed basis-function set to its display label(s).
    # "linear" = translational and rotational functions (x, y, z, Rx, Ry, Rz)
    # "quadratic" = products of two coordinates (x², xy, xz, …)
    _assign("z",      ["z"],            "linear")
    _assign("xy",     ["x", "y"],       "linear")
    _assign("Rz",     ["Rz"],           "linear")
    _assign("Rxy",    ["Rx", "Ry"],     "linear")
    _assign("z2",     ["z²"],           "quadratic")
    _assign("x2py2",  ["x²+y²"],        "quadratic")
    _assign("x2y2xy", ["x²-y²", "xy"],  "quadratic")
    _assign("xzyz",   ["xz", "yz"],     "quadratic")

    return result
