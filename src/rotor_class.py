"""
Rotor classification by principal moment of inertia degeneracy.
Translated from the original C++ `schoenflies` (was reference/src/symmetry/
rotor_class.h; that vendored tree was removed in 0.2.0 — see
https://gitlab.com/lkkmpn/schoenflies).

Background
----------
Every molecule has three *principal moments of inertia* Ia ≤ Ib ≤ Ic,
obtained by diagonalising the inertia tensor.  The pattern of degeneracy
among these three values tells us which rotational symmetry axes are
physically possible, and therefore constrains the search for symmetry
operations.

For example, a spherical top (Ia = Ib = Ic) has no preferred axis at all,
so any direction is a candidate rotation axis.  A linear molecule has
Ia ≈ 0, so the only meaningful axis is the molecular axis itself.
"""

from enum import Enum, auto


class RotorClass(Enum):
    """Rigid-rotor type determined from the degeneracy of the principal moments of inertia.

    The classification determines which symmetry axes are worth searching for
    (see Symmetry._axis_inertially_allowed).

    Members
    -------
    AsymmetricTop
        Ia < Ib < Ic — all three moments are distinct.
        No rotational symmetry axis is required.  Examples: water (C2v),
        hydrogen peroxide (C2).
    OblateSymmetricTop
        Ia ≈ Ib < Ic — the two smaller moments are equal; the unique axis
        is the *short* (oblate / "disc-like") axis.  Examples: benzene (D6h),
        ammonia (C3v).
    ProlateSymmetricTop
        Ia < Ib ≈ Ic — the two larger moments are equal; the unique axis is
        the *long* (prolate / "cigar-like") axis.  Examples: chloromethane (C3v),
        allene (D2d).
    Linear
        Ia ≈ 0, Ib ≈ Ic — the molecule lies along a single axis; rotation
        about that axis produces zero moment.  Examples: CO2 (D∞h), HCN (C∞v).
    SphericalTop
        Ia ≈ Ib ≈ Ic — all three moments equal; the molecule has no preferred
        orientation.  Examples: methane (Td), sulfur hexafluoride (Oh).
    """

    AsymmetricTop = auto()       # Ia < Ib < Ic
    OblateSymmetricTop = auto()  # Ia ≈ Ib < Ic  (disc-like, e.g. benzene)
    ProlateSymmetricTop = auto() # Ia < Ib ≈ Ic  (cigar-like, e.g. CH3Cl)
    Linear = auto()              # Ia ≈ 0, Ib ≈ Ic  (special prolate limit)
    SphericalTop = auto()        # Ia ≈ Ib ≈ Ic  (e.g. CH4, SF6)
