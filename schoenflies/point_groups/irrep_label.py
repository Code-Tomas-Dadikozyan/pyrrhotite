"""
IrrepLabel: encodes a Mulliken irreducible representation symbol.

Reading Mulliken symbols
------------------------
An irrep label like A1g, B2u, E′, or T2g encodes several pieces of
information about how functions (orbitals, vibrations) transform:

  Letter (Mulliken symbol) — the degeneracy:
    A — singly degenerate, symmetric under the principal rotation Cn
        (character +1 under Cn)
    B — singly degenerate, antisymmetric under Cn
        (character -1 under Cn)
    E — doubly degenerate (2D irrep); the two basis functions are related
        by the symmetry and cannot be separated
    T — triply degenerate (3D); seen in cubic/octahedral groups
    G — quadruply degenerate (4D); seen in icosahedral group Ih
    H — quintuply degenerate (5D); seen in icosahedral group Ih

  Subscript number (1 or 2, sometimes higher):
    For A and B: 1 means symmetric under a C2 axis perpendicular to the
    principal axis (or under σv), 2 means antisymmetric.
    For E, T, …: just a sequential index when multiple of the same type exist.

  Parity (g/u) — only in groups with an inversion centre:
    g (gerade)   — symmetric under inversion: χ(i) = +dimension
    u (ungerade) — antisymmetric:             χ(i) = -dimension

  Prime modifier (′/″) — only in groups without inversion but with σh:
    ′  — symmetric under σh: χ(σh) = +dimension
    ″  — antisymmetric under σh: χ(σh) = -dimension

Example: A1g in Oh (octahedral) is the totally symmetric, non-degenerate,
gerade representation — the "breathing" mode of an octahedral molecule.
"""

from __future__ import annotations

from enum import Enum


class IrrepLabel:
    """Label for an irreducible representation using Mulliken notation."""

    class Mulliken(Enum):
        """Mulliken symbol encoding the degeneracy of the representation.

        The letter is the primary indicator of how many-dimensional the
        irrep is and whether it is symmetric (A) or antisymmetric (B)
        under the principal rotation axis.
        """
        SingleSymmetric = 0       # A: 1D, symmetric under Cn (χ(Cn) = +1)
        SingleAntisymmetric = 1   # B: 1D, antisymmetric under Cn (χ(Cn) = -1)
        DoublyDegenerate = 2      # E: 2D pair of degenerate functions
        TriplyDegenerate = 3      # T: 3D triple; found in cubic groups (T, O, I)
        QuadruplyDegenerate = 4   # G: 4D; found in icosahedral groups
        QuintuplyDegenerate = 5   # H: 5D; found in icosahedral groups

        # Short single-letter aliases matching the conventional notation
        A = 0
        B = 1
        E = 2
        T = 3
        G = 4
        H = 5

    class Parity(Enum):
        """Symmetry with respect to a centre of inversion.

        Only relevant for groups containing i (inversion).  The parity
        describes whether the basis function is preserved (g) or negated (u)
        when all coordinates are reflected through the origin.
        """
        none = 0
        Gerade = 1    # g: symmetric under inversion, χ(i) = +dimension
        Ungerade = 2  # u: antisymmetric, χ(i) = -dimension

        # Short aliases
        g = 1
        u = 2

    class Prime(Enum):
        """Symmetry with respect to a horizontal mirror plane σh.

        Used in groups (e.g. Cnh, Dnh with odd n) that contain σh but not i.
        A single prime (′) means the function is symmetric under σh; double
        prime (″) means antisymmetric.
        """
        none = 0
        Single = 1    # ′: symmetric under σh
        Double = 2    # ″: antisymmetric under σh

    def __init__(
        self,
        mulliken: IrrepLabel.Mulliken,
        subscript: int = 0,
        parity: IrrepLabel.Parity | None = None,
        prime: IrrepLabel.Prime | None = None,
    ) -> None:
        """Construct an IrrepLabel with optional subscript, parity, and prime.

        Mirrors C++ overloaded constructors: if a Parity is passed as the second
        positional argument (subscript position), it is re-routed to parity.
        If a Prime is passed in the subscript or parity position, it is re-routed
        to prime.  This allows point_groups.py to use compact positional calls
        matching the C++ source style.
        """
        if isinstance(subscript, IrrepLabel.Parity):
            parity = subscript
            subscript = 0
        elif isinstance(subscript, IrrepLabel.Prime):
            prime = subscript
            subscript = 0
        if isinstance(parity, IrrepLabel.Prime):
            prime = parity
            parity = None

        self._mulliken = mulliken
        self._subscript = subscript
        self._parity = parity if parity is not None else IrrepLabel.Parity.none
        self._prime = prime if prime is not None else IrrepLabel.Prime.none

    # ------------------------------------------------------------------
    # Factory classmethods mirroring C++ overloaded constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_mulliken(cls, mulliken: IrrepLabel.Mulliken) -> IrrepLabel:
        """Create a label from a Mulliken symbol only."""
        return cls(mulliken)

    @classmethod
    def from_mulliken_subscript(cls, mulliken: IrrepLabel.Mulliken, subscript: int) -> IrrepLabel:
        """Create a label from a Mulliken symbol and integer subscript."""
        return cls(mulliken, subscript=subscript)

    @classmethod
    def from_mulliken_parity(cls, mulliken: IrrepLabel.Mulliken, parity: IrrepLabel.Parity) -> IrrepLabel:
        """Create a label from a Mulliken symbol and parity."""
        return cls(mulliken, parity=parity)

    @classmethod
    def from_mulliken_subscript_parity(
        cls, mulliken: IrrepLabel.Mulliken, subscript: int, parity: IrrepLabel.Parity
    ) -> IrrepLabel:
        """Create a label from a Mulliken symbol, subscript, and parity."""
        return cls(mulliken, subscript=subscript, parity=parity)

    @classmethod
    def from_mulliken_prime(cls, mulliken: IrrepLabel.Mulliken, prime: IrrepLabel.Prime) -> IrrepLabel:
        """Create a label from a Mulliken symbol and prime."""
        return cls(mulliken, prime=prime)

    @classmethod
    def from_mulliken_subscript_prime(
        cls, mulliken: IrrepLabel.Mulliken, subscript: int, prime: IrrepLabel.Prime
    ) -> IrrepLabel:
        """Create a label from a Mulliken symbol, subscript, and prime."""
        return cls(mulliken, subscript=subscript, prime=prime)

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------

    def get_mulliken(self) -> IrrepLabel.Mulliken:
        """Return the Mulliken symbol."""
        return self._mulliken

    def get_subscript(self) -> int:
        """Return the integer subscript (0 means no subscript)."""
        return self._subscript

    def get_parity(self) -> IrrepLabel.Parity:
        """Return the inversion parity."""
        return self._parity

    def get_prime(self) -> IrrepLabel.Prime:
        """Return the prime modifier."""
        return self._prime

    # ------------------------------------------------------------------
    # Name helpers
    # ------------------------------------------------------------------

    def get_name(self) -> str:
        """Return the plaintext Mulliken label (e.g. 'A1g', 'T2u', 'E′')."""
        match self._mulliken:
            case IrrepLabel.Mulliken.SingleSymmetric:
                name = "A"
            case IrrepLabel.Mulliken.SingleAntisymmetric:
                name = "B"
            case IrrepLabel.Mulliken.DoublyDegenerate:
                name = "E"
            case IrrepLabel.Mulliken.TriplyDegenerate:
                name = "T"
            case IrrepLabel.Mulliken.QuadruplyDegenerate:
                name = "G"
            case IrrepLabel.Mulliken.QuintuplyDegenerate:
                name = "H"
            case _:
                raise RuntimeError("Unexpected Mulliken symbol encountered.")

        if self._subscript > 0:
            name += str(self._subscript)

        if self._parity != IrrepLabel.Parity.none:
            match self._parity:
                case IrrepLabel.Parity.Gerade:
                    name += "g"
                case IrrepLabel.Parity.Ungerade:
                    name += "u"
                case _:
                    raise RuntimeError("Unexpected parity encountered.")

        if self._prime != IrrepLabel.Prime.none:
            match self._prime:
                case IrrepLabel.Prime.Single:
                    name += "′"
                case IrrepLabel.Prime.Double:
                    name += "″"
                case _:
                    raise RuntimeError("Unexpected prime encountered.")

        return name

    def get_name_html(self) -> str:
        """Return the HTML-formatted Mulliken label."""
        match self._mulliken:
            case IrrepLabel.Mulliken.SingleSymmetric:
                name = "A"
            case IrrepLabel.Mulliken.SingleAntisymmetric:
                name = "B"
            case IrrepLabel.Mulliken.DoublyDegenerate:
                name = "E"
            case IrrepLabel.Mulliken.TriplyDegenerate:
                name = "T"
            case IrrepLabel.Mulliken.QuadruplyDegenerate:
                name = "G"
            case IrrepLabel.Mulliken.QuintuplyDegenerate:
                name = "H"
            case _:
                raise RuntimeError("Unexpected Mulliken symbol encountered.")

        subscript_str = ""
        if self._subscript > 0:
            subscript_str += str(self._subscript)

        if self._parity != IrrepLabel.Parity.none:
            match self._parity:
                case IrrepLabel.Parity.Gerade:
                    subscript_str += "g"
                case IrrepLabel.Parity.Ungerade:
                    subscript_str += "u"
                case _:
                    raise RuntimeError("Unexpected parity encountered.")

        if subscript_str:
            name += "<sub>" + subscript_str + "</sub>"

        if self._prime != IrrepLabel.Prime.none:
            match self._prime:
                case IrrepLabel.Prime.Single:
                    name += "′"
                case IrrepLabel.Prime.Double:
                    name += "″"
                case _:
                    raise RuntimeError("Unexpected prime encountered.")

        return name
