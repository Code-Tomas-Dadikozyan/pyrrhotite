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
        # Algorithm: start with the total count of found operations, then
        # subtract one for each operation that the group *requires*.
        # If any required type is missing entirely, return -1 immediately.
        # Whatever remains after all subtractions is the "surplus" — extra
        # operations we found that this group does not need.  A surplus of 0
        # is a perfect match; a small positive surplus is a near-match.
        # The caller picks the group with the smallest non-negative surplus.
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

    def print_character_table(self, *, complex: bool = False, plain: bool = False) -> None:
        """Print the character table to stdout.

        Parameters
        ----------
        complex:
            When True, split each real 2D E-type irrep into two complex 1D rows
            showing ε^(jk) and ε^*(jk) characters (only for pure cyclic / Sn groups
            where this is meaningful; other groups fall back to real rows).
        plain:
            When True, use the plain-text formatter regardless of whether `rich`
            is installed.  When False (default), use the `rich` table renderer for
            a cleaner, terminal-width-aware layout; falls back to plain text if
            `rich` is not available.
        """
        import sys
        import math as _math

        # ------------------------------------------------------------------
        # Shared helpers
        # ------------------------------------------------------------------

        def _safe(text: str) -> str:
            # Some terminals (Windows cmd, certain SSH sessions) cannot encode
            # the Unicode characters used in Schoenflies/Mulliken notation.
            # We try to encode the string first; if that raises an exception
            # we fall back to ASCII-safe substitutions so output is never garbled.
            # Substitutions:  σ→s, ∞→inf, ′→', ″→'', −→-, ε→e, ²→^2, ¹→(nothing)
            try:
                text.encode(sys.stdout.encoding or "utf-8")
                return text
            except (UnicodeEncodeError, LookupError):
                return (text
                        .replace("σ", "s").replace("∞", "inf")
                        .replace("′", "'").replace("″", "''")
                        .replace("−", "-").replace("ε", "e")
                        .replace("²", "^2").replace("¹", ""))

        def fmt(v: float) -> str:
            # Format a single character-table value for display.
            # Three rules, tried in order:
            #   1. If the value matches a known irrational constant (e.g. √2, φ),
            #      return the symbolic name — avoids ugly floats like "1.4142".
            #   2. If the value is an exact integer (e.g. 1.0, -1.0, 2.0),
            #      return the integer string — "1" not "1.0000".
            #   3. Otherwise, show 4 decimal places and strip trailing zeros.
            sym = _float_to_symbol(v)
            if sym is not None:
                return sym
            return str(int(v)) if v == int(v) else f"{v:.4f}".rstrip("0")

        # ------------------------------------------------------------------
        # Complex-mode helpers
        # ------------------------------------------------------------------

        def _eps_symbol(exp: int, n: int) -> str:
            """Return symbolic ε^exp for the group of order n (ε = e^(2πi/n))."""
            e = exp % n
            if e == 0:
                return "1"
            if e == n // 2 and n % 2 == 0:
                return "-1"
            return "ε" if e == 1 else f"ε^{e}"

        def _is_pure_cyclic() -> bool:
            """True if this group has no reflections and no inversion (Cn or Sn)."""
            return self._num_reflections == 0 and self._num_inversions == 0

        def _group_order_n() -> int | None:
            """Infer n from the principal-axis column (first unique op), or None."""
            if not self._unique_operations:
                return None
            lbl = self._unique_operations[0].get_label()
            from ..operations.operation_label import OperationLabel as _OL
            if lbl.get_element() in (_OL.Element.ProperRotation, _OL.Element.ImproperRotation):
                return lbl.get_degree()
            return None

        def _build_rows() -> list[tuple[str, list[str]]]:
            """Build the list of (row_label, [cell_strings]) for the table body.

            Each irrep normally produces one row.  In *complex mode* (enabled
            when `complex=True` and the group is a pure cyclic/Sn group), each
            doubly-degenerate E_j irrep is instead split into two complex
            conjugate rows:
                top row  — characters ε^(jk), where ε = e^(2πi/n)
                bottom row — characters ε^(-jk) (= complex conjugate)
            This is the "complex character table" form used in some textbooks
            to make the E-type characters look like 1D representations.
            The label of the top row gets a "{" suffix to visually pair the rows.

            For non-E irreps (A, B) and for groups where complex mode does not
            apply, each irrep gives a single real-valued row using the `fmt`
            formatter.
            """
            rows: list[tuple[str, list[str]]] = []
            use_complex = complex and _is_pure_cyclic()
            n = _group_order_n() if use_complex else None

            for irrep, char_row in zip(self._irreps, self._characters):
                label = _safe(irrep.get_name())
                is_e_type = (irrep.get_mulliken() == IrrepLabel.Mulliken.E)

                if use_complex and is_e_type and n is not None:
                    # Recover j (the E-type index) from the irrep subscript.
                    # E1 → j=1, E2 → j=2, …  A single E with no subscript → j=1.
                    sub = irrep.get_subscript()
                    j = sub if sub else 1
                    row_top: list[str] = ["1"]   # χ(E) = 1 for both conjugate rows
                    row_bot: list[str] = ["1"]
                    for rc in self._unique_operations:
                        from ..operations.operation_label import OperationLabel as _OL
                        elem = rc.get_label().get_element()
                        if elem in (_OL.Element.ProperRotation, _OL.Element.ImproperRotation):
                            k = rc.get_label().get_multiple() or 1
                            d = rc.get_label().get_degree()
                            # Convert (degree d, multiple k) to the S_n power index p.
                            # Each step of degree d corresponds to n/d steps of the
                            # fundamental S_n rotation, so p = k * (n // d).
                            p = k * (n // d) if n else k
                            row_top.append(_safe(_eps_symbol(j * p, n)))
                            row_bot.append(_safe(_eps_symbol(-j * p, n)))
                        else:
                            # Non-rotation columns (σ, i) have real characters;
                            # use the stored float value directly.
                            idx = self._unique_operations.index(rc)
                            row_top.append(fmt(char_row[idx + 1]))
                            row_bot.append(fmt(char_row[idx + 1]))
                    rows.append((f"{label}{{", row_top))
                    rows.append(("", row_bot))
                else:
                    cells = [fmt(v) for v in char_row]
                    rows.append((label, cells))
            return rows

        col_headers = ["E"] + [_safe(olc.get_short_name()) for olc in self._unique_operations]
        name = _safe(self._label.get_name())
        data_rows = _build_rows()

        # ------------------------------------------------------------------
        # Basis function columns
        # ------------------------------------------------------------------
        from .basis_functions import compute_basis_functions
        try:
            bf = compute_basis_functions(self)
        except Exception:
            bf = {}

        lin_col: list[str] = []
        quad_col: list[str] = []
        for label, _ in data_rows:
            clean = label.rstrip("{").strip()
            lin_col.append(_safe(", ".join(bf.get(clean, {}).get("linear", []))))
            quad_col.append(_safe(", ".join(bf.get(clean, {}).get("quadratic", []))))

        has_bf = any(v for v in lin_col) or any(v for v in quad_col)

        # ------------------------------------------------------------------
        # Plain-text renderer
        # ------------------------------------------------------------------

        def _render_plain() -> None:
            """Render the character table as a plain-text fixed-width grid.

            Layout:
              - `row_w` : width of the leftmost "irrep label" column
              - `col_w` : list of widths, one per character table column
              - Each cell is right-aligned within its column width.
              - Columns are separated by " | ".
              - If basis functions were computed, two extra columns
                ("Lin/Rot" and "Quadratic") are appended.
            """
            row_labels = [r[0] for r in data_rows]
            row_w = max((len(r) for r in row_labels), default=4)

            def _col_width(h: str, col_vals: list[str]) -> int:
                # Minimum width of 6 ensures that values like "-1" and "2cos(π/7)"
                # always fit without truncation and columns are never unreadably thin.
                return max(len(h), 6, max((len(v) for v in col_vals), default=1))

            col_w = [_col_width("E", [r[1][0] for r in data_rows])]
            for ci, h in enumerate(col_headers[1:], start=1):
                col_vals = [r[1][ci] if ci < len(r[1]) else "" for r in data_rows]
                col_w.append(_col_width(h, col_vals))

            extra_headers = (["Lin/Rot", "Quadratic"] if has_bf else [])
            lin_w  = max(len("Lin/Rot"),  max((len(v) for v in lin_col),  default=1)) if has_bf else 0
            quad_w = max(len("Quadratic"), max((len(v) for v in quad_col), default=1)) if has_bf else 0

            parts = [f"{name:{row_w}}"]
            for h, w in zip(col_headers, col_w):
                parts.append(f"{h:>{w}}")
            if has_bf:
                parts.append(f"{'Lin/Rot':>{lin_w}}")
                parts.append(f"{'Quadratic':>{quad_w}}")
            header = " | ".join(parts)
            print(header)
            print("-" * len(header))

            for (rl, cells), lv, qv in zip(data_rows, lin_col, quad_col):
                row_parts = [f"{rl:{row_w}}"]
                for ci, w in enumerate(col_w):
                    row_parts.append(f"{(cells[ci] if ci < len(cells) else ''):>{w}}")
                if has_bf:
                    row_parts.append(f"{lv:>{lin_w}}")
                    row_parts.append(f"{qv:>{quad_w}}")
                print(" | ".join(row_parts))

        # ------------------------------------------------------------------
        # Rich renderer
        # ------------------------------------------------------------------

        def _render_rich() -> None:
            """Render the character table using the `rich` library for a
            cleaner, terminal-width-aware layout with aligned columns and
            styled headers.

            `rich` is an optional dependency.  If it is not installed, this
            function raises ImportError and the caller falls back to
            `_render_plain()`.  The `box.SIMPLE_HEAVY` style draws a heavy
            header separator and no outer border, which suits dense tabular data.
            """
            from rich.table import Table
            from rich import box
            from rich.console import Console

            table = Table(
                title=name,
                box=box.SIMPLE_HEAVY,
                show_header=True,
                header_style="bold",
                title_style="bold cyan",
            )
            table.add_column("Irrep", style="bold", no_wrap=True)
            for h in col_headers:
                table.add_column(h, justify="right", no_wrap=True)
            if has_bf:
                table.add_column("Lin / Rot", justify="left", style="dim")
                table.add_column("Quadratic", justify="left", style="dim")

            for (rl, cells), lv, qv in zip(data_rows, lin_col, quad_col):
                row = [rl] + [cells[i] if i < len(cells) else "" for i in range(len(col_headers))]
                if has_bf:
                    row += [lv, qv]
                table.add_row(*row)

            Console().print(table)

        # ------------------------------------------------------------------
        # Dispatch
        # ------------------------------------------------------------------

        if plain:
            _render_plain()
            return

        try:
            _render_rich()
        except ImportError:
            _render_plain()
