from __future__ import annotations

from enum import Enum


class PointGroupLabel:
    """Label for a crystallographic point group, encoding class and order."""

    class Class(Enum):
        """Point-group family."""
        # classes with order
        C = 0       # cyclic
        Ch = 1      # reflection
        Cv = 2      # pyramidal
        S = 3       # improper rotation
        D = 4       # dihedral
        Dh = 5      # prismatic
        Dd = 6      # antiprismatic

        # classes without order (polyhedral)
        T = 7       # chiral tetrahedral
        Td = 8      # achiral tetrahedral
        Th = 9      # pyritohedral
        O = 10      # chiral octahedral
        Oh = 11     # achiral octahedral
        I = 12      # chiral icosahedral
        Ih = 13     # achiral icosahedral

        # special cases
        Cs = 14     # Cs = C1h
        Ci = 15     # Ci = S2
        Cinfv = 16  # C∞v (linear, no inversion)
        Dinfh = 17  # D∞h (linear, with inversion)

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
    # Getters
    # ------------------------------------------------------------------

    def get_class(self) -> PointGroupLabel.Class:
        """Return the point-group class."""
        return self._class

    def get_order(self) -> int:
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

    def get_name(self) -> str:
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

    def get_name_html(self) -> str:
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
    def get_class_from_string(class_string: str) -> PointGroupLabel.Class:
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
