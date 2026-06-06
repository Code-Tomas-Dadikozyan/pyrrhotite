"""
PointGroupLabel: encodes a Schoenflies point group symbol.

The 18 classes and how to read them
-------------------------------------
Schoenflies point groups fall into five broad categories:

  Axial groups  — have one principal rotation axis of finite order n.
    Cn   (cyclic)        — just the Cn axis; no mirrors, no C2.  Chiral.
                           Examples: C2 (H2O2 twisted), C3 (chiral propeller).
    Cnh  (reflection)    — Cn axis + horizontal mirror σh.
                           Examples: C2h (trans-N2H2), C3h (boric acid B(OH)3).
    Cnv  (pyramidal)     — Cn axis + n vertical mirrors σv.
                           Examples: C2v (water), C3v (ammonia), C4v (SF5Cl).
    Sn   (improper)      — only an Sn axis; no independent Cn or σ.
                           Examples: S4 (1,3,5,7-tetramethylcyclooctatetraene),
                                     S6 (staggered ethane geometry).
    Dn   (dihedral)      — Cn axis + n horizontal C2 axes.  Chiral.
                           Examples: D2 (twisted allene), D3 (tris-chelate).
    Dnh  (prismatic)     — Dn + σh (and therefore also σv/σd and i for even n).
                           Examples: D2h (ethylene), D3h (BF3), D6h (benzene).
    Dnd  (antiprismatic) — Dn + σd planes bisecting C2 pairs; also has S_{2n}.
                           Examples: D2d (allene), D3d (staggered ethane).

  Polyhedral groups  — based on the five Platonic solids; no principal axis.
    T    — chiral tetrahedral (4 C3, 3 C2).  Example: C(CHFClBr)4 in theory.
    Td   — achiral tetrahedral (adds σd, S4).  Example: methane, SiCl4.
    Th   — pyritohedral (T + inversion; adds S6, σh).  Example: pyrite FeS2.
    O    — chiral octahedral (3 C4, 4 C3, 6 C2).  Example: chiral cage.
    Oh   — achiral octahedral (O + i, σ planes).  Example: SF6, [Co(en)3]^3+.
    I    — chiral icosahedral (6 C5, 10 C3, 15 C2).  Example: chiral fullerene.
    Ih   — achiral icosahedral (I + i).  Example: C60 buckminsterfullerene.

  Special low-symmetry groups
    Cs   — only a single mirror plane σ (= C1h = S1).
           Examples: CHFClBr molecule in a specific conformation.
    Ci   — only inversion centre i (= S2).
           Example: staggered meso-tartaric acid.

  Linear groups  — infinite-order rotation axis (C∞).
    C∞v  — linear, no inversion.  Example: HCN, HF, CO.
    D∞h  — linear, with inversion.  Example: CO2, H2, N2.

The Class enum stores these 18 classes as integers.  The integer values have
no physical meaning — they are just stable identifiers.
"""

from __future__ import annotations

from enum import Enum


class PointGroupLabel:
    """Label for a crystallographic point group, encoding class and order."""

    class Class(Enum):
        """Point-group family (18 Schoenflies classes).

        Axial groups (need an order n ≥ 1)
        -----------
        C   — cyclic: only a Cn rotation axis
        Ch  — Cnh: Cn + horizontal mirror σh
        Cv  — Cnv: Cn + vertical mirrors σv
        S   — Sn: only an improper rotation axis (n even, n ≥ 4)
        D   — Dn: Cn + n horizontal C2 axes
        Dh  — Dnh: Dn + σh (+ i for even n)
        Dd  — Dnd: Dn + dihedral mirrors σd (+ S_{2n})

        Polyhedral groups (order field is unused)
        -----------------
        T   — chiral tetrahedral (order 12)
        Td  — full tetrahedral (order 24)
        Th  — pyritohedral (order 24)
        O   — chiral octahedral (order 24)
        Oh  — full octahedral (order 48)
        I   — chiral icosahedral (order 60)
        Ih  — full icosahedral (order 120)

        Special low-symmetry (order field is unused)
        ---------------------------
        Cs  — only a mirror plane (= C1h)
        Ci  — only an inversion centre (= S2)

        Linear (order field is unused)
        ------
        Cinfv  — C∞v: linear, no inversion
        Dinfh  — D∞h: linear, with inversion
        """
        # classes with order
        C = 0       # cyclic: Cn
        Ch = 1      # Cnh: Cn + σh
        Cv = 2      # Cnv: Cn + σv (pyramidal)
        S = 3       # Sn: improper rotation axis only
        D = 4       # Dn: Cn + n×C2 (dihedral)
        Dh = 5      # Dnh: Dn + σh (prismatic)
        Dd = 6      # Dnd: Dn + σd (antiprismatic)

        # classes without order (polyhedral)
        T = 7       # chiral tetrahedral (T ≅ A4)
        Td = 8      # full tetrahedral   (Td ≅ S4)
        Th = 9      # pyritohedral       (Th ≅ A4 × Z2)
        O = 10      # chiral octahedral  (O ≅ S4)
        Oh = 11     # full octahedral    (Oh ≅ S4 × Z2)
        I = 12      # chiral icosahedral (I ≅ A5)
        Ih = 13     # full icosahedral   (Ih ≅ A5 × Z2)

        # special cases (degenerate axial groups)
        Cs = 14     # Cs = C1h: single mirror only
        Ci = 15     # Ci = S2:  inversion only
        Cinfv = 16  # C∞v: linear, no inversion (e.g. HCN)
        Dinfh = 17  # D∞h: linear, with inversion (e.g. CO2)

    _STRING_TO_CLASS: dict[str, PointGroupLabel.Class] = {}  # populated after class definition

    def __init__(self, point_group_class: PointGroupLabel.Class, order: int = 0) -> None:
        """Construct a PointGroupLabel; order is ignored for polyhedral classes."""
        self._class = point_group_class
        self._order = order

    # ------------------------------------------------------------------
    # Factory classmethods mirroring C++ overloaded constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_class(cls, point_group_class: PointGroupLabel.Class) -> PointGroupLabel:
        """Create a label from a class only (order=0)."""
        return cls(point_group_class)

    @classmethod
    def from_class_order(cls, point_group_class: PointGroupLabel.Class, order: int) -> PointGroupLabel:
        """Create a label from a class and order."""
        return cls(point_group_class, order)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def group_class(self) -> PointGroupLabel.Class:
        """Return the point-group class."""
        return self._class

    @property
    def order(self) -> int:
        """Return the order (0 for polyhedral and special cases)."""
        return self._order

    # ------------------------------------------------------------------
    # Classification predicates
    # ------------------------------------------------------------------

    def is_cyclic(self) -> bool:
        """Return True for C, Ch, Cv, S, Cs, Ci groups."""
        return self._class in (
            PointGroupLabel.Class.C,
            PointGroupLabel.Class.Ch,
            PointGroupLabel.Class.Cv,
            PointGroupLabel.Class.S,
            PointGroupLabel.Class.Cs,
            PointGroupLabel.Class.Ci,
        )

    def is_dihedral(self) -> bool:
        """Return True for D, Dh, Dd groups."""
        return self._class in (
            PointGroupLabel.Class.D,
            PointGroupLabel.Class.Dh,
            PointGroupLabel.Class.Dd,
        )

    def is_polyhedral(self) -> bool:
        """Return True for T, Td, Th, O, Oh, I, Ih groups."""
        return self._class in (
            PointGroupLabel.Class.T,
            PointGroupLabel.Class.Td,
            PointGroupLabel.Class.Th,
            PointGroupLabel.Class.O,
            PointGroupLabel.Class.Oh,
            PointGroupLabel.Class.I,
            PointGroupLabel.Class.Ih,
        )

    def is_tetrahedral(self) -> bool:
        """Return True for T, Td, Th groups."""
        return self._class in (
            PointGroupLabel.Class.T,
            PointGroupLabel.Class.Td,
            PointGroupLabel.Class.Th,
        )

    def is_octahedral(self) -> bool:
        """Return True for O, Oh groups."""
        return self._class in (PointGroupLabel.Class.O, PointGroupLabel.Class.Oh)

    def is_icosahedral(self) -> bool:
        """Return True for I, Ih groups."""
        return self._class in (PointGroupLabel.Class.I, PointGroupLabel.Class.Ih)

    def is_linear(self) -> bool:
        """Return True for C∞v, D∞h groups."""
        return self._class in (PointGroupLabel.Class.Cinfv, PointGroupLabel.Class.Dinfh)

    # ------------------------------------------------------------------
    # Matching
    # ------------------------------------------------------------------

    def matches(self, other: PointGroupLabel) -> bool:
        """Return True if labels refer to the same point group (order-insensitive for polyhedral)."""
        if self.is_polyhedral():
            return self._class == other._class
        return self._class == other._class and self._order == other._order

    # ------------------------------------------------------------------
    # Name helpers
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Return the plaintext name (e.g. 'C3v', 'D2h', 'Td', 'C∞v', 'D∞h')."""
        order = str(self._order)
        match self._class:
            case PointGroupLabel.Class.C:
                return "C" + order
            case PointGroupLabel.Class.Ch:
                return "C" + order + "h"
            case PointGroupLabel.Class.Cv:
                return "C" + order + "v"
            case PointGroupLabel.Class.S:
                return "S" + order
            case PointGroupLabel.Class.D:
                return "D" + order
            case PointGroupLabel.Class.Dh:
                return "D" + order + "h"
            case PointGroupLabel.Class.Dd:
                return "D" + order + "d"
            case PointGroupLabel.Class.T:
                return "T"
            case PointGroupLabel.Class.Td:
                return "Td"
            case PointGroupLabel.Class.Th:
                return "Th"
            case PointGroupLabel.Class.O:
                return "O"
            case PointGroupLabel.Class.Oh:
                return "Oh"
            case PointGroupLabel.Class.I:
                return "I"
            case PointGroupLabel.Class.Ih:
                return "Ih"
            case PointGroupLabel.Class.Cs:
                return "Cs"
            case PointGroupLabel.Class.Ci:
                return "Ci"
            case PointGroupLabel.Class.Cinfv:
                return "C∞v"
            case PointGroupLabel.Class.Dinfh:
                return "D∞h"
            case _:
                raise RuntimeError("Unexpected point group class encountered.")

    @property
    def name_html(self) -> str:
        """Return the HTML-formatted name."""
        order = str(self._order)
        match self._class:
            case PointGroupLabel.Class.C:
                return "<i>C</i><sub>" + order + "</sub>"
            case PointGroupLabel.Class.Ch:
                return "<i>C</i><sub>" + order + "h</sub>"
            case PointGroupLabel.Class.Cv:
                return "<i>C</i><sub>" + order + "v</sub>"
            case PointGroupLabel.Class.S:
                return "<i>S</i><sub>" + order + "</sub>"
            case PointGroupLabel.Class.D:
                return "<i>D</i><sub>" + order + "</sub>"
            case PointGroupLabel.Class.Dh:
                return "<i>D</i><sub>" + order + "h</sub>"
            case PointGroupLabel.Class.Dd:
                return "<i>D</i><sub>" + order + "d</sub>"
            case PointGroupLabel.Class.T:
                return "<i>T</i>"
            case PointGroupLabel.Class.Td:
                return "<i>T</i><sub>d</sub>"
            case PointGroupLabel.Class.Th:
                return "<i>T</i><sub>h</sub>"
            case PointGroupLabel.Class.O:
                return "<i>O</i>"
            case PointGroupLabel.Class.Oh:
                return "<i>O</i><sub>h</sub>"
            case PointGroupLabel.Class.I:
                return "<i>I</i>"
            case PointGroupLabel.Class.Ih:
                return "<i>I</i><sub>h</sub>"
            case PointGroupLabel.Class.Cs:
                return "<i>C</i><sub>s</sub>"
            case PointGroupLabel.Class.Ci:
                return "<i>C</i><sub>i</sub>"
            case PointGroupLabel.Class.Cinfv:
                return "<i>C</i><sub>∞v</sub>"
            case PointGroupLabel.Class.Dinfh:
                return "<i>D</i><sub>∞h</sub>"
            case _:
                raise RuntimeError("Unexpected point group class encountered.")

    # ------------------------------------------------------------------
    # Static helper
    # ------------------------------------------------------------------

    @staticmethod
    def class_from_string(class_string: str) -> PointGroupLabel.Class:
        """Return the Class enum value corresponding to a string key."""
        mapping = {
            "C": PointGroupLabel.Class.C,
            "Ch": PointGroupLabel.Class.Ch,
            "Cv": PointGroupLabel.Class.Cv,
            "S": PointGroupLabel.Class.S,
            "D": PointGroupLabel.Class.D,
            "Dh": PointGroupLabel.Class.Dh,
            "Dd": PointGroupLabel.Class.Dd,
            "T": PointGroupLabel.Class.T,
            "Td": PointGroupLabel.Class.Td,
            "Th": PointGroupLabel.Class.Th,
            "O": PointGroupLabel.Class.O,
            "Oh": PointGroupLabel.Class.Oh,
            "I": PointGroupLabel.Class.I,
            "Ih": PointGroupLabel.Class.Ih,
            "Cs": PointGroupLabel.Class.Cs,
            "Ci": PointGroupLabel.Class.Ci,
            "Cinfv": PointGroupLabel.Class.Cinfv,
            "Dinfh": PointGroupLabel.Class.Dinfh,
        }
        if class_string not in mapping:
            raise RuntimeError("Invalid class encountered: " + class_string)
        return mapping[class_string]


# Module-level alias used by operation_manager and other importers
PGClass = PointGroupLabel.Class
