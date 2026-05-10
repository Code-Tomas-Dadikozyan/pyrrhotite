from __future__ import annotations

from enum import Enum


class OperationLabel:
    """Label for a symmetry operation, encoding element, degree, multiple, plane, and prime."""

    DEGREE_INF: int = 0  # sentinel for infinite-order axes (C∞, S∞)

    class Element(Enum):
        """Symmetry element type."""
        ProperRotation = 0
        Inversion = 1
        ImproperRotation = 2
        Reflection = 3

        # aliases
        C = 0
        I = 1
        S = 2
        sigma = 3

    class Plane(Enum):
        """Mirror-plane orientation."""
        none = 0
        Horizontal = 1
        Vertical = 2
        Dihedral = 3

        # aliases
        h = 1
        v = 2
        d = 3

    class Prime(Enum):
        """Prime modifier distinguishing similar operations."""
        none = 0
        Single = 1
        Double = 2

    def __init__(
        self,
        element: OperationLabel.Element,
        degree: int = 0,
        multiple: int = 1,
        plane: OperationLabel.Plane | None = None,
        prime: OperationLabel.Prime | None = None,
    ) -> None:
        """Construct an OperationLabel with optional degree, multiple, plane, and prime."""
        self._element = element
        self._degree = degree
        self._multiple = multiple
        self._plane = plane if plane is not None else OperationLabel.Plane.none
        self._prime = prime if prime is not None else OperationLabel.Prime.none

    # ------------------------------------------------------------------
    # Factory classmethods mirroring C++ overloaded constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_element(cls, element: OperationLabel.Element) -> OperationLabel:
        """Create a label from element only (degree=0, multiple=1)."""
        return cls(element)

    @classmethod
    def from_element_degree(cls, element: OperationLabel.Element, degree: int) -> OperationLabel:
        """Create a label from element and degree."""
        return cls(element, degree=degree)

    @classmethod
    def from_element_degree_multiple(
        cls, element: OperationLabel.Element, degree: int, multiple: int
    ) -> OperationLabel:
        """Create a label from element, degree, and multiple."""
        return cls(element, degree=degree, multiple=multiple)

    @classmethod
    def from_element_degree_prime(
        cls, element: OperationLabel.Element, degree: int, prime: OperationLabel.Prime
    ) -> OperationLabel:
        """Create a label from element, degree, and prime."""
        return cls(element, degree=degree, prime=prime)

    @classmethod
    def from_element_plane(
        cls, element: OperationLabel.Element, plane: OperationLabel.Plane
    ) -> OperationLabel:
        """Create a label from element and plane (degree=0)."""
        return cls(element, plane=plane)

    @classmethod
    def from_element_plane_prime(
        cls,
        element: OperationLabel.Element,
        plane: OperationLabel.Plane,
        prime: OperationLabel.Prime,
    ) -> OperationLabel:
        """Create a label from element, plane, and prime."""
        return cls(element, plane=plane, prime=prime)

    # ------------------------------------------------------------------
    # Getters / setters
    # ------------------------------------------------------------------

    def get_element(self) -> OperationLabel.Element:
        """Return the symmetry element."""
        return self._element

    def get_degree(self) -> int:
        """Return the degree of the symmetry axis (0 == infinite)."""
        return self._degree

    def get_multiple(self) -> int:
        """Return the multiple of the degree."""
        return self._multiple

    def set_multiple(self, multiple: int) -> None:
        """Set the multiple of the degree."""
        self._multiple = multiple

    def get_plane(self) -> OperationLabel.Plane:
        """Return the mirror-plane orientation."""
        return self._plane

    def set_plane(self, plane: OperationLabel.Plane) -> None:
        """Set the mirror-plane orientation."""
        self._plane = plane

    def get_prime(self) -> OperationLabel.Prime:
        """Return the prime modifier."""
        return self._prime

    def set_prime(self, prime: OperationLabel.Prime) -> None:
        """Set the prime modifier."""
        self._prime = prime

    # ------------------------------------------------------------------
    # Name helpers
    # ------------------------------------------------------------------

    def _format_number(self, number: int) -> str:
        """Format an integer for display, using Unicode minus for negatives."""
        if number < 0:
            return "−" + str(abs(number))
        return str(number)

    def _get_name_suffix(self) -> str:
        """Return the verbose suffix (' rotation', ' inversion', etc.)."""
        match self._element:
            case OperationLabel.Element.ProperRotation:
                return " rotation"
            case OperationLabel.Element.Inversion:
                return " inversion"
            case OperationLabel.Element.ImproperRotation:
                return " improper rotation"
            case OperationLabel.Element.Reflection:
                return " reflection"
            case _:
                raise RuntimeError("Unexpected symmetry element encountered.")

    def get_short_name(self) -> str:
        """Return the short plaintext name (e.g. 'C3^2', 'σv')."""
        degree_str = self._format_number(self._degree)
        multiple_str = self._format_number(self._multiple)

        match self._element:
            case OperationLabel.Element.ProperRotation:
                symbol = "C"
            case OperationLabel.Element.Inversion:
                symbol = "i"
            case OperationLabel.Element.ImproperRotation:
                symbol = "S"
            case OperationLabel.Element.Reflection:
                symbol = "σ"
            case _:
                raise RuntimeError("Unexpected symmetry element encountered.")

        name = symbol

        if self._element in (OperationLabel.Element.ProperRotation, OperationLabel.Element.ImproperRotation):
            name += "∞" if self._degree == self.DEGREE_INF else degree_str
            if self._multiple != 1:
                name += "^" + multiple_str

        if self._element == OperationLabel.Element.Reflection and self._plane != OperationLabel.Plane.none:
            match self._plane:
                case OperationLabel.Plane.Horizontal:
                    name += "h"
                case OperationLabel.Plane.Vertical:
                    name += "v"
                case OperationLabel.Plane.Dihedral:
                    name += "d"
                case _:
                    raise RuntimeError("Unexpected symmetry plane encountered.")

        if self._prime != OperationLabel.Prime.none:
            match self._prime:
                case OperationLabel.Prime.Single:
                    name += "′"
                case OperationLabel.Prime.Double:
                    name += "″"
                case _:
                    raise RuntimeError("Unexpected symmetry prime encountered.")

        return name

    def get_short_name_html(self) -> str:
        """Return the short HTML-formatted name."""
        degree_str = self._format_number(self._degree)
        multiple_str = self._format_number(self._multiple)

        match self._element:
            case OperationLabel.Element.ProperRotation:
                symbol = "<i>C</i>"
            case OperationLabel.Element.Inversion:
                symbol = "<i>i</i>"
            case OperationLabel.Element.ImproperRotation:
                symbol = "<i>S</i>"
            case OperationLabel.Element.Reflection:
                symbol = "<i>σ</i>"
            case _:
                raise RuntimeError("Unexpected symmetry element encountered.")

        name = symbol

        if self._element in (OperationLabel.Element.ProperRotation, OperationLabel.Element.ImproperRotation):
            name += "<sub>∞</sub>" if self._degree == self.DEGREE_INF else "<sub>" + degree_str + "</sub>"
            if self._multiple != 1:
                name += "<sup>" + multiple_str + "</sup>"

        if self._element == OperationLabel.Element.Reflection and self._plane != OperationLabel.Plane.none:
            match self._plane:
                case OperationLabel.Plane.Horizontal:
                    name += "<sub>h</sub>"
                case OperationLabel.Plane.Vertical:
                    name += "<sub>v</sub>"
                case OperationLabel.Plane.Dihedral:
                    name += "<sub>d</sub>"
                case _:
                    raise RuntimeError("Unexpected symmetry plane encountered.")

        if self._prime != OperationLabel.Prime.none:
            match self._prime:
                case OperationLabel.Prime.Single:
                    name += "′"
                case OperationLabel.Prime.Double:
                    name += "″"
                case _:
                    raise RuntimeError("Unexpected symmetry prime encountered.")

        return name

    def get_name(self) -> str:
        """Return the full plaintext name (short name + verbose suffix)."""
        return self.get_short_name() + self._get_name_suffix()

    def get_name_html(self) -> str:
        """Return the full HTML-formatted name (short HTML name + verbose suffix)."""
        return self.get_short_name_html() + self._get_name_suffix()

    # ------------------------------------------------------------------
    # Matching
    # ------------------------------------------------------------------

    def matches(self, other: OperationLabel) -> bool:
        """Return True if labels match ignoring the multiple field."""
        return (
            self._element == other._element
            and self._degree == other._degree
            and self._plane == other._plane
            and self._prime == other._prime
        )

    def matches_strict(self, other: OperationLabel) -> bool:
        """Return True if labels match including abs(multiple)."""
        return self.matches(other) and (
            self._multiple == other._multiple or self._multiple == -other._multiple
        )
