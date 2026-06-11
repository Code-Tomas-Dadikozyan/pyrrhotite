"""
Registry for discovered symmetry operations; validates, deduplicates, and
generates the final point-group operation list.
Direct translation of reference/src/symmetry/operations/operation_manager.h/cpp.
"""

from __future__ import annotations

import copy
import math
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

    @property
    def operations(self) -> list[Operation]:
        """Return the mutable list of all found operations."""
        return self._operations

    @property
    def inversions(self) -> list[Operation]:
        """Return all found inversion operations."""
        return [op for op in self._operations
                if op.label.element == OperationLabel.Element.Inversion]

    @property
    def proper_rotations(self) -> list[Operation]:
        """Return all found proper rotation operations."""
        return [op for op in self._operations
                if op.label.element == OperationLabel.Element.ProperRotation]

    @property
    def improper_rotations(self) -> list[Operation]:
        """Return all found improper rotation operations."""
        return [op for op in self._operations
                if op.label.element == OperationLabel.Element.ImproperRotation]

    @property
    def reflections(self) -> list[Operation]:
        """Return all found reflection operations."""
        return [op for op in self._operations
                if op.label.element == OperationLabel.Element.Reflection]

    @property
    def point_group_operations(self) -> dict[int, Operation]:
        """Return the id→operation map for the final labelled point-group set."""
        return self._point_group_operations

    def point_group_operation(self, id: int) -> Operation:
        """Return a single point-group operation by ID."""
        try:
            return self._point_group_operations[id]
        except KeyError:
            raise RuntimeError(f"Invalid operation ID encountered: {id}")

    @property
    def point_group_operations_order(self) -> list[OperationGroup]:
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
                if operation.error < existing.error:
                    self._operations[i] = operation
                return True

        self._operations.append(operation)
        return True

    def _check_operation(self, operation: Operation) -> bool:
        """Run the operation on the structure and return True if its error is below threshold.

        The base 0.1 threshold is an empirical value from the reference C++
        implementation.  It is large enough to accept operations whose
        validity is obscured by XYZ coordinate rounding (typical precision
        is 3-4 decimal places, giving errors up to ~0.001 Å), but small
        enough to reject candidate axes that genuinely do not map atoms onto
        atoms (errors typically >> 0.1 Å for wrong axes).

        For high-order Cn/Sn candidates (degree >= 8) the angular spacing
        between Cn and its neighbouring orders shrinks below what the base
        threshold can distinguish (e.g. C9's 40 degree spacing is only 5
        degrees away from a C8 candidate at 45 degrees, giving an error of
        ~0.087 — under 0.1). The threshold is tightened to half the angular
        gap to the next-higher order, pi / (degree * (degree + 1)), so that
        a wrong-order candidate next to a genuine high-order axis is rejected
        while the genuine axis (error ~ 0) is unaffected.
        """
        operation.do_operation(self._structure)
        threshold = 0.1
        if operation.degree >= 8:
            threshold = min(threshold, math.pi / (operation.degree * (operation.degree + 1)))
        return operation.error < threshold

    # ------------------------------------------------------------------
    # Point-group operation generation
    # ------------------------------------------------------------------

    def generate_point_group_operations(self, point_group: PointGroup) -> None:
        """Populate point_group_operations and point_group_operations_order.

        Iterates the unique operations defined in the point group and generates
        all concrete operations (including rotation multiples) for display.
        """
        for label_count in point_group.unique_operations:
            self._generate_operations_by_label(point_group, label_count.label)

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

        pg_class = point_group.label.group_class
        elem = operation_label.element
        deg = operation_label.degree

        is_infinite_group = pg_class in (PGClass.Cinfv, PGClass.Dinfh)
        # In C∞v and D∞h, there are infinitely many C2′ axes (perpendicular to
        # the molecular axis) and infinitely many σv planes.  We cannot enumerate
        # them all, so instead we insert a single placeholder group marked as
        # having "infinite multiplicity" — enough for display purposes.
        # `is_infinite_op` selects exactly those two operation types: degree-2
        # proper rotations (the C2′ axes) and any reflection (the σv planes).
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
                self._point_group_operations[match.id] = match
                operation_group.add_operation_id(match.id)
        else:
            # Determine which multiples to generate.
            # For a Cn axis with n > 2, the character table has one column for
            # each conjugacy class {Cn^k, Cn^(n-k)}.  Both Cn^k (forward) and
            # Cn^(n-k) = Cn^(-k) (backward/inverse) are physically distinct
            # operations even though they are in the same class, so we generate
            # both (+multiple and -multiple) to populate the display list.
            # For C2 the inverse of C2^1 is C2^1 itself (a half-turn is its own
            # inverse), so only one multiple is needed.
            base_multiple = operation_label.multiple
            if deg > 2:
                multiples = [base_multiple, -base_multiple]
            else:
                multiples = [base_multiple]

            for multiple in multiples:
                for match in matches:
                    if multiple == match.label.multiple:
                        self._point_group_operations[match.id] = match
                        operation_group.add_operation_id(match.id)
                    else:
                        op_copy = self._copy_operation(match)
                        op_copy.label.set_multiple(multiple)
                        self._point_group_operations[op_copy.id] = op_copy
                        operation_group.add_operation_id(op_copy.id)

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
            elem = op.label.element
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

        # Fallback for terminals that cannot render Schoenflies Unicode symbols.
        def _safe(text: str) -> str:
            try:
                text.encode(sys.stdout.encoding or "utf-8")
                return text
            except (UnicodeEncodeError, LookupError):
                return (text
                        .replace("σ", "s").replace("∞", "inf")
                        .replace("′", "'").replace("″", "''")
                        .replace("−", "-"))

        # Format a 3-vector as "(+x.xxx, +y.yyy, +z.zzz)" for axis display.
        def _fmt_vec(v: object) -> str:
            return f"({v[0]:+.3f}, {v[1]:+.3f}, {v[2]:+.3f})"

        E = OperationLabel.Element
        n = self._structure.num_atoms
        name_w = 10  # column width for operation name

        print(_safe(f"{'Operation':<{name_w}}  {'Axis / Normal':<26}  Notes"))
        print("─" * 70)

        for group in self._point_group_operations_order:
            if group.infinite_multiplicity:
                label = group._operation_label
                print(_safe(f"{label.short_name + ' (∞)':<{name_w}}  {'':26}"))
                continue

            for op_id in group.operation_ids:
                if op_id not in self._point_group_operations:
                    continue
                op = self._point_group_operations[op_id]
                elem = op.label.element
                short = _safe(op.label.short_name)
                notes_parts: list[str] = []

                if elem == E.Inversion:
                    axis_str = "—"
                elif elem in (E.ProperRotation, E.ImproperRotation):
                    axis_str = _fmt_vec(op.axis)
                    on_axis = op.atoms_on_axis(self._structure)
                    if on_axis:
                        notes_parts.append(f"{len(on_axis)}/{n} atoms on axis")
                elif elem == E.Reflection:
                    axis_str = f"n={_fmt_vec(op.axis)}"
                    in_plane = op.atoms_in_plane(self._structure)
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
        op_copy.id = self._next_id
        self._next_id += 1
        return op_copy
