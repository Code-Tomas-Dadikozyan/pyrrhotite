from __future__ import annotations

from typing import TYPE_CHECKING

from ..operations.operation_label import OperationLabel
from ..operations.operation_label_count import OperationLabelCount
from .irrep_label import IrrepLabel
from .point_group_label import PointGroupLabel

if TYPE_CHECKING:
    from ..operations.operation import Operation


class PointGroup:
    """A crystallographic point group with its symmetry operations, irreps, and character table."""

    def __init__(
        self,
        label: PointGroupLabel,
        order: int,
        num_inversions: int,
        num_proper_rotations: dict[int, int],
        num_improper_rotations: dict[int, int],
        num_reflections: int,
        unique_operations: list[OperationLabelCount],
        irreps: list[IrrepLabel],
        characters: list[list[float]],
    ) -> None:
        """Construct a PointGroup with full symmetry data.

        For rotation counts, degenerate rotations around the same axis (e.g. C3 and
        C3^2) are counted once — degree is the key in num_proper/improper_rotations.
        """
        self._label = label
        self._order = order
        self._num_inversions = num_inversions
        self._num_proper_rotations = num_proper_rotations
        self._num_improper_rotations = num_improper_rotations
        self._num_reflections = num_reflections
        self._unique_operations = unique_operations
        self._irreps = irreps
        self._characters = characters

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------

    def get_label(self) -> PointGroupLabel:
        """Return the point-group label."""
        return self._label

    def get_order(self) -> int:
        """Return the total number of unique symmetry operations."""
        return self._order

    def get_unique_operations(self) -> list[OperationLabelCount]:
        """Return the list of unique operation labels with counts."""
        return self._unique_operations

    def get_irreps(self) -> list[IrrepLabel]:
        """Return the irreducible representations of this point group."""
        return self._irreps

    def get_characters(self) -> list[list[float]]:
        """Return the character table indexed as [irrep][operation class]."""
        return self._characters

    # ------------------------------------------------------------------
    # Core matching function used by the symmetry-determination algorithm
    # ------------------------------------------------------------------

    def compare_to_symmetry_operations(self, operations: list[Operation]) -> int:
        """Compare this point group against a list of found symmetry operations.

        Returns -1 if any required operation type is absent, or a non-negative
        integer counting how many found operations are not required by this group
        (the surplus).  The caller selects the group with the smallest surplus.
        """
        # start with total found; subtract each required class that matches
        num_remaining = len(operations)

        # count inversions and reflections in the found set
        num_inversions = 0
        num_reflections = 0
        for op in operations:
            element = op.get_label().get_element()
            if element == OperationLabel.Element.Inversion:
                num_inversions += 1
            if element == OperationLabel.Element.Reflection:
                num_reflections += 1

        if num_inversions < self._num_inversions:
            return -1
        num_remaining -= self._num_inversions

        if num_reflections < self._num_reflections:
            return -1
        num_remaining -= self._num_reflections

        # check proper rotations per degree
        for degree, num_required in self._num_proper_rotations.items():
            num_found = sum(
                1 for op in operations
                if op.get_label().get_element() == OperationLabel.Element.ProperRotation
                and op.get_degree() == degree
            )
            if num_found < num_required:
                return -1
            num_remaining -= num_required

        # check improper rotations per degree
        for degree, num_required in self._num_improper_rotations.items():
            num_found = sum(
                1 for op in operations
                if op.get_label().get_element() == OperationLabel.Element.ImproperRotation
                and op.get_degree() == degree
            )
            if num_found < num_required:
                return -1
            num_remaining -= num_required

        return num_remaining
