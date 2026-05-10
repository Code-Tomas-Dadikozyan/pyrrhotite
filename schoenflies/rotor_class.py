"""
Rotor classification by principal moment of inertia degeneracy.
Direct translation of reference/src/symmetry/rotor_class.h.
"""

from enum import Enum, auto


class RotorClass(Enum):
    """Rigid-rotor type determined from the degeneracy of the principal moments of inertia."""

    AsymmetricTop = auto()       # Ia < Ib < Ic
    OblateSymmetricTop = auto()  # Ia ≈ Ib < Ic
    ProlateSymmetricTop = auto() # Ia < Ib ≈ Ic
    Linear = auto()              # Ia << Ib ≈ Ic  (special prolate limit)
    SphericalTop = auto()        # Ia ≈ Ib ≈ Ic
