from __future__ import annotations

from .operation_label import OperationLabel


class OperationGroup:
    """Groups symmetry operations sharing the same OperationLabel, tracking their IDs."""

    def __init__(self, operation_label: OperationLabel) -> None:
        """Construct an OperationGroup from the shared label."""
        self._operation_label = operation_label
        self._operation_ids: list[int] = []
        self._infinite_multiplicity: bool = False

    # ------------------------------------------------------------------
    # Properties / setters
    # ------------------------------------------------------------------

    @property
    def operation_ids(self) -> list[int]:
        """Return the list of operation IDs in this group."""
        return self._operation_ids

    @property
    def infinite_multiplicity(self) -> bool:
        """Return whether this group has infinite multiplicity."""
        return self._infinite_multiplicity

    def add_operation_id(self, id: int) -> None:
        """Append an operation ID to this group."""
        self._operation_ids.append(id)

    def set_infinite_multiplicity(self, infinite_multiplicity: bool) -> None:
        """Set whether this group has infinite multiplicity."""
        self._infinite_multiplicity = infinite_multiplicity

    @property
    def num_operations(self) -> int:
        """Return the number of operations in this group."""
        return len(self._operation_ids)

    # ------------------------------------------------------------------
    # Name helpers
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Return the plaintext group name with multiplicity annotation."""
        name = self._operation_label.name
        n = len(self._operation_ids)
        if n > 1 or self._infinite_multiplicity:
            count = "∞" if self._infinite_multiplicity else str(n)
            name += "s (" + count + ")"
        return name

    @property
    def name_html(self) -> str:
        """Return the HTML-formatted group name with multiplicity annotation."""
        name = self._operation_label.name_html
        n = len(self._operation_ids)
        if n > 1 or self._infinite_multiplicity:
            count = "∞" if self._infinite_multiplicity else str(n)
            name += "s (" + count + ")"
        return name
