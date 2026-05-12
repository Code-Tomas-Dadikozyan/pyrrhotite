from __future__ import annotations

import math
from typing import TYPE_CHECKING

from ..operations.operation_label import OperationLabel

# ---------------------------------------------------------------------------
# Symbolic display for irrational character-table values
# ---------------------------------------------------------------------------
# Each entry: (positive float value, symbol string).
# Covers every 2cos(nπ/m) constant that appears in the hardcoded point groups.
# Matching is tried for both x and -x; negatives get a leading "−".
_SYMBOL_TABLE: list[tuple[float, str]] = [
    (2.0 * math.cos(math.pi / 4),   "√2"),           # ≈ 1.4142  (C4, D4h, …)
    (2.0 * math.cos(math.pi / 5),   "φ"),             # ≈ 1.6180  golden ratio (Ih)
    (2.0 * math.cos(2 * math.pi / 5), "φ−1"),         # ≈ 0.6180  (Ih, C5v, …)
    (2.0 * math.cos(math.pi / 6),   "√3"),            # ≈ 1.7321  (C6, D6h, …)
    (2.0 * math.cos(math.pi / 7),   "2cos(π/7)"),     # ≈ 1.8019  (C7, D7, …)
    (2.0 * math.cos(2 * math.pi / 7), "2cos(2π/7)"),  # ≈ 1.2470
    (2.0 * math.cos(3 * math.pi / 7), "2cos(3π/7)"),  # ≈ 0.4450
    (2.0 * math.cos(math.pi / 8),   "2cos(π/8)"),     # ≈ 1.8478  (C8, S8, …)
    (2.0 * math.cos(3 * math.pi / 8), "2cos(3π/8)"),  # ≈ 0.7654
    (2.0 * math.cos(math.pi / 9),   "2cos(π/9)"),     # ≈ 1.8794  (C9, …)
    (2.0 * math.cos(2 * math.pi / 9), "2cos(2π/9)"),  # ≈ 1.5321
    (2.0 * math.cos(4 * math.pi / 9), "2cos(4π/9)"),  # ≈ 0.3473
    (2.0 * math.cos(math.pi / 10),  "2cos(π/10)"),    # ≈ 1.9021  (C10, …)
    (2.0 * math.cos(3 * math.pi / 10), "2cos(3π/10)"),# ≈ 1.1756
]
_SYMBOL_TOL = 1e-4


def _float_to_symbol(v: float) -> str | None:
    """Return a symbolic string for v if it matches a known irrational constant, else None."""
    for val, sym in _SYMBOL_TABLE:
        if abs(v - val) < _SYMBOL_TOL:
            return sym
        if abs(v + val) < _SYMBOL_TOL:
            return "−" + sym
    return None
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

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def print_character_table(self) -> None:
        """Print the character table to stdout in a human-readable grid format."""
        import sys

        def _safe(text: str) -> str:
            """Replace characters that cannot be encoded in the terminal's codec."""
            try:
                text.encode(sys.stdout.encoding or "utf-8")
                return text
            except (UnicodeEncodeError, LookupError):
                return (text
                        .replace("σ", "s").replace("∞", "inf")
                        .replace("′", "'").replace("″", "''")
                        .replace("−", "-"))

        name = _safe(self._label.get_name())
        col_headers = [_safe(olc.get_short_name()) for olc in self._unique_operations]
        row_headers = [_safe(ir.get_name()) for ir in self._irreps]

        row_w = max((len(r) for r in row_headers), default=4)

        # format a character value: symbolic > integer > decimal
        def fmt(v: float) -> str:
            sym = _float_to_symbol(v)
            if sym is not None:
                return sym
            return str(int(v)) if v == int(v) else f"{v:.4f}".rstrip("0")

        # column widths: at least as wide as the header, 6, or the widest formatted value
        def _col_width(h: str, char_col: list[float]) -> int:
            max_val_w = max((len(fmt(v)) for v in char_col), default=1)
            return max(len(h), 6, max_val_w)

        col_w = [_col_width(h, [row[j] for row in self._characters])
                 for j, h in enumerate(col_headers)]

        header = f"{name:{row_w}} | " + " | ".join(
            f"{h:>{w}}" for h, w in zip(col_headers, col_w)
        )
        separator = "-" * len(header)

        print(header)
        print(separator)
        for row_label, char_row in zip(row_headers, self._characters):
            values = " | ".join(
                f"{fmt(v):>{w}}" for v, w in zip(char_row, col_w)
            )
            print(f"{row_label:{row_w}} | {values}")
