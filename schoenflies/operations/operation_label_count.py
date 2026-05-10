from __future__ import annotations

from .operation_label import OperationLabel


class OperationLabelCount:
    """Pairs an OperationLabel with the count of how many such operations exist."""

    COUNT_INF: int = 0  # sentinel for infinite multiplicity (C∞v, D∞h)

    def __init__(self, label: OperationLabel, count: int = 1) -> None:
        """Construct an OperationLabelCount with a label and optional count (default 1)."""
        self._label = label
        self._count = count

    # ------------------------------------------------------------------
    # Factory classmethods mirroring C++ overloaded constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_label(cls, label: OperationLabel) -> OperationLabelCount:
        """Create an OperationLabelCount with count=1."""
        return cls(label, count=1)

    @classmethod
    def from_count_and_label(cls, count: int, label: OperationLabel) -> OperationLabelCount:
        """Create an OperationLabelCount with explicit count."""
        return cls(label, count=count)

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------

    def get_count(self) -> int:
        """Return the number of operations with this label (0 == infinite)."""
        return self._count

    def get_label(self) -> OperationLabel:
        """Return the operation label."""
        return self._label

    # ------------------------------------------------------------------
    # Name helpers
    # ------------------------------------------------------------------

    def _get_count_prefix(self) -> str:
        """Return the count prefix string ('N ', '∞ ', or '')."""
        if self._count > 1:
            return str(self._count) + " "
        if self._count == self.COUNT_INF:
            return "∞ "
        return ""

    def get_name(self) -> str:
        """Return the full plaintext name including count prefix and plural 's'."""
        plural = "s" if self._count > 1 else ""
        return self._get_count_prefix() + self._label.get_name() + plural

    def get_name_html(self) -> str:
        """Return the full HTML-formatted name including count prefix and plural 's'."""
        plural = "s" if self._count > 1 else ""
        return self._get_count_prefix() + self._label.get_name_html() + plural

    def get_short_name(self) -> str:
        """Return the short plaintext name including count prefix."""
        return self._get_count_prefix() + self._label.get_short_name()

    def get_short_name_html(self) -> str:
        """Return the short HTML-formatted name including count prefix."""
        return self._get_count_prefix() + self._label.get_short_name_html()
