from __future__ import annotations

from .operation_label import OperationLabel


class OperationLabelCount:
    """Pairs an OperationLabel with the count of how many such operations exist."""

    COUNT_INF: int = 0  # sentinel for infinite multiplicity (C∞v, D∞h)

    def __init__(self, count: int, label: OperationLabel) -> None:
        """Construct an OperationLabelCount with a count and label."""
        self._count = count
        self._label = label

    # ------------------------------------------------------------------
    # Factory classmethods mirroring C++ overloaded constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_label(cls, label: OperationLabel) -> OperationLabelCount:
        """Create an OperationLabelCount with count=1."""
        return cls(1, label)

    @classmethod
    def from_count_and_label(cls, count: int, label: OperationLabel) -> OperationLabelCount:
        """Create an OperationLabelCount with explicit count."""
        return cls(count, label)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def count(self) -> int:
        """Return the number of operations with this label (0 == infinite)."""
        return self._count

    @property
    def label(self) -> OperationLabel:
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

    @property
    def name(self) -> str:
        """Return the full plaintext name including count prefix and plural 's'."""
        plural = "s" if self._count > 1 else ""
        return self._get_count_prefix() + self._label.name + plural

    @property
    def name_html(self) -> str:
        """Return the full HTML-formatted name including count prefix and plural 's'."""
        plural = "s" if self._count > 1 else ""
        return self._get_count_prefix() + self._label.name_html + plural

    @property
    def short_name(self) -> str:
        """Return the short plaintext name including count prefix."""
        return self._get_count_prefix() + self._label.short_name

    @property
    def short_name_html(self) -> str:
        """Return the short HTML-formatted name including count prefix."""
        return self._get_count_prefix() + self._label.short_name_html
