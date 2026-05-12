"""
Registry for discovered symmetry operations; validates, deduplicates, and
generates the final point-group operation list.
Direct translation of reference/src/symmetry/operations/operation_manager.h/cpp.
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from .operation import Operation
from .operation_group import OperationGroup
from .operation_label import OperationLabel

if TYPE_CHECKING:
    from ..structure import Structure
    from ..point_groups.point_group import PointGroup


class OperationManager:
    """Stores found symmetry operations and generates the final labelled set."""

    def __init__(self, structure: Structure) -> None:
        """Initialise with the molecule whose symmetry is being determined."""
        self._structure = structure
        self._next_id: int = 1
        self._operations: list[Operation] = []
        self._point_group_operations: dict[int, Operation] = {}
        self._point_group_operations_order: list[OperationGroup] = []

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_operations(self) -> list[Operation]:
        """Return the mutable list of all found operations."""
        return self._operations

    def get_inversions(self) -> list[Operation]:
        """Return all found inversion operations."""
        return [op for op in self._operations
                if op.label.get_element() == OperationLabel.Element.Inversion]

    def get_proper_rotations(self) -> list[Operation]:
        """Return all found proper rotation operations."""
        return [op for op in self._operations
                if op.label.get_element() == OperationLabel.Element.ProperRotation]

    def get_improper_rotations(self) -> list[Operation]:
        """Return all found improper rotation operations."""
        return [op for op in self._operations
                if op.label.get_element() == OperationLabel.Element.ImproperRotation]

    def get_reflections(self) -> list[Operation]:
        """Return all found reflection operations."""
        return [op for op in self._operations
                if op.label.get_element() == OperationLabel.Element.Reflection]

    def get_point_group_operations(self) -> dict[int, Operation]:
        """Return the id→operation map for the final labelled point-group set."""
        return self._point_group_operations

    def get_point_group_operation(self, id: int) -> Operation:
        """Return a single point-group operation by ID."""
        try:
            return self._point_group_operations[id]
        except KeyError:
            raise RuntimeError(f"Invalid operation ID encountered: {id}")

    def get_point_group_operations_order(self) -> list[OperationGroup]:
        """Return the ordered list of operation groups for the point group."""
        return self._point_group_operations_order

    # ------------------------------------------------------------------
    # Adding operations
    # ------------------------------------------------------------------

    def add_operation(self, operation: Operation) -> bool:
        """Validate an operation against the structure; add it if it passes.

        Returns True if the operation is a valid symmetry operation (error < 0.1),
        regardless of whether it was already present.
        Deduplicates: if an equal operation exists but this one has lower error,
        the existing entry is replaced.
        """
        if not self._check_operation(operation):
            return False

        operation.set_id(self._next_id)
        self._next_id += 1

        for i, existing in enumerate(self._operations):
            if operation == existing:
                if operation.get_error() < existing.get_error():
                    self._operations[i] = operation
                return True

        self._operations.append(operation)
        return True

    def _check_operation(self, operation: Operation) -> bool:
        """Run the operation on the structure and return True if error < 0.1."""
        operation.do_operation(self._structure)
        return operation.get_error() < 0.1

    # ------------------------------------------------------------------
    # Point-group operation generation
    # ------------------------------------------------------------------

    def generate_point_group_operations(self, point_group: PointGroup) -> None:
        """Populate point_group_operations and point_group_operations_order.

        Iterates the unique operations defined in the point group and generates
        all concrete operations (including rotation multiples) for display.
        """
        for label_count in point_group.get_unique_operations():
            self._generate_operations_by_label(point_group, label_count.get_label())

    def _generate_operations_by_label(
        self, point_group: PointGroup, operation_label: OperationLabel
    ) -> None:
        """Generate all concrete operations matching operation_label.

        Handles two special cases for C∞v and D∞h (infinite C2' and σv groups):
        those are delegated to _generate_infinite_operation_group.
        For all other labels, finds matching found operations and expands
        rotation multiples (+m and −m for degree > 2).
        """
        from ..point_groups.point_group_label import PGClass

        pg_class = point_group.get_label().get_class()
        elem = operation_label.get_element()
        deg = operation_label.get_degree()

        is_infinite_group = pg_class in (PGClass.Cinfv, PGClass.Dinfh)
        is_infinite_op = (
            elem == OperationLabel.Element.ProperRotation and deg == 2
            or elem == OperationLabel.Element.Reflection
        )
        if is_infinite_group and is_infinite_op:
            self._generate_infinite_operation_group(operation_label)
            return

        operation_group = OperationGroup(operation_label)

        matches = [op for op in self._operations if op.label.matches(operation_label)]

        if elem in (OperationLabel.Element.Inversion, OperationLabel.Element.Reflection):
            for match in matches:
                self._point_group_operations[match.get_id()] = match
                operation_group.add_operation_id(match.get_id())
        else:
            # Determine which multiples to generate
            base_multiple = operation_label.get_multiple()
            if deg > 2:
                multiples = [base_multiple, -base_multiple]
            else:
                multiples = [base_multiple]

            for multiple in multiples:
                for match in matches:
                    if multiple == match.label.get_multiple():
                        self._point_group_operations[match.get_id()] = match
                        operation_group.add_operation_id(match.get_id())
                    else:
                        op_copy = self._copy_operation(match)
                        op_copy.label.set_multiple(multiple)
                        self._point_group_operations[op_copy.get_id()] = op_copy
                        operation_group.add_operation_id(op_copy.get_id())

        self._point_group_operations_order.append(operation_group)

    def _generate_infinite_operation_group(self, operation_label: OperationLabel) -> None:
        """Add a placeholder group for the infinitely-degenerate C2'/σv in C∞v/D∞h."""
        operation_group = OperationGroup(operation_label)
        operation_group.set_infinite_multiplicity(True)
        self._point_group_operations_order.append(operation_group)

    # ------------------------------------------------------------------
    # Structured output
    # ------------------------------------------------------------------

    def summarize(self) -> dict[str, list[Operation]]:
        """Return point-group operations grouped by symmetry element type.

        Keys are the standard symbols: "Cn", "Sn", "i", "σ".
        Only keys with at least one operation are included.
        Call after generate_point_group_operations().
        """
        E = OperationLabel.Element
        buckets: dict[str, list[Operation]] = {"Cn": [], "Sn": [], "i": [], "σ": []}
        for op in self._point_group_operations.values():
            elem = op.get_label().get_element()
            if elem == E.ProperRotation:
                buckets["Cn"].append(op)
            elif elem == E.ImproperRotation:
                buckets["Sn"].append(op)
            elif elem == E.Inversion:
                buckets["i"].append(op)
            elif elem == E.Reflection:
                buckets["σ"].append(op)
        return {k: v for k, v in buckets.items() if v}

    def print_operations(self) -> None:
        """Print all point-group operations with geometric annotation.

        For each operation shows:
          - Its short name (e.g. C3, σv, C2′)
          - Axis direction for rotations, plane normal for reflections
          - How many atoms lie on the axis / in the plane
          - [molecular plane] tag when a reflection contains every atom

        Call after generate_point_group_operations().
        """
        import sys

        def _safe(text: str) -> str:
            try:
                text.encode(sys.stdout.encoding or "utf-8")
                return text
            except (UnicodeEncodeError, LookupError):
                return (text
                        .replace("σ", "s").replace("∞", "inf")
                        .replace("′", "'").replace("″", "''")
                        .replace("−", "-"))

        def _fmt_vec(v: object) -> str:
            return f"({v[0]:+.3f}, {v[1]:+.3f}, {v[2]:+.3f})"

        E = OperationLabel.Element
        n = self._structure.num_atoms
        name_w = 10  # column width for operation name

        print(_safe(f"{'Operation':<{name_w}}  {'Axis / Normal':<26}  Notes"))
        print("─" * 70)

        for group in self._point_group_operations_order:
            if group.get_infinite_multiplicity():
                label = group._operation_label
                print(_safe(f"{label.get_short_name() + ' (∞)':<{name_w}}  {'':26}"))
                continue

            for op_id in group.get_operation_ids():
                if op_id not in self._point_group_operations:
                    continue
                op = self._point_group_operations[op_id]
                elem = op.get_label().get_element()
                short = _safe(op.get_label().get_short_name())
                notes_parts: list[str] = []

                if elem == E.Inversion:
                    axis_str = "—"
                elif elem in (E.ProperRotation, E.ImproperRotation):
                    axis_str = _fmt_vec(op.get_axis())
                    on_axis = op.get_atoms_on_axis(self._structure)
                    if on_axis:
                        notes_parts.append(f"{len(on_axis)}/{n} atoms on axis")
                elif elem == E.Reflection:
                    axis_str = f"n={_fmt_vec(op.get_axis())}"
                    in_plane = op.get_atoms_in_plane(self._structure)
                    notes_parts.append(f"{len(in_plane)}/{n} atoms in plane")
                    if op.is_molecular_plane(self._structure):
                        notes_parts.append("[molecular plane]")
                else:
                    axis_str = ""

                notes = "  ".join(notes_parts)
                print(_safe(f"{short:<{name_w}}  {axis_str:<26}  {notes}"))

    def _copy_operation(self, operation: Operation) -> Operation:
        """Return a deep copy of operation with a fresh ID."""
        op_copy = copy.deepcopy(operation)
        op_copy.set_id(self._next_id)
        self._next_id += 1
        return op_copy
