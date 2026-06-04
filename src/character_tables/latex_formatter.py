"""
LaTeX formatter for Schoenflies point group character tables.

Inline API
----------
    from pyrrhotite.character_tables import format_latex, save_latex

    print(format_latex(["C3v", "D6h"]))
    path = save_latex(["Oh"], "oh_table.tex")

CLI
---
    python -m pyrrhotite.character_tables.latex_formatter C3v D6h
    python -m pyrrhotite.character_tables.latex_formatter Oh --save
    python -m pyrrhotite.character_tables.latex_formatter Oh D4h --save tables.tex

Required LaTeX packages: booktabs, amsmath
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..operations.operation_label import OperationLabel
from ..operations.operation_label_count import OperationLabelCount
from ..point_groups.irrep_label import IrrepLabel
from ..point_groups.point_group import PointGroup
from ..point_groups.point_group_label import PointGroupLabel
from .generator import get_or_generate_point_group, parse_point_group_name

# ---------------------------------------------------------------------------
# Label → LaTeX helpers
# ---------------------------------------------------------------------------

_MULLIKEN_LETTER: dict[IrrepLabel.Mulliken, str] = {
    IrrepLabel.Mulliken.SingleSymmetric:    "A",
    IrrepLabel.Mulliken.SingleAntisymmetric: "B",
    IrrepLabel.Mulliken.DoublyDegenerate:   "E",
    IrrepLabel.Mulliken.TriplyDegenerate:   "T",
    IrrepLabel.Mulliken.QuadruplyDegenerate: "G",
    IrrepLabel.Mulliken.QuintuplyDegenerate: "H",
}


def _irrep_latex(ir: IrrepLabel) -> str:
    """Return a LaTeX math-mode string for an IrrepLabel, e.g. ``$A_{1g}$``."""
    letter = _MULLIKEN_LETTER[ir.get_mulliken()]

    sub = ""
    if ir.get_subscript() > 0:
        sub += str(ir.get_subscript())
    match ir.get_parity():
        case IrrepLabel.Parity.Gerade:
            sub += "g"
        case IrrepLabel.Parity.Ungerade:
            sub += "u"

    body = letter + ("_{" + sub + "}" if sub else "")

    match ir.get_prime():
        case IrrepLabel.Prime.Single:
            prime = "'"
        case IrrepLabel.Prime.Double:
            prime = "''"
        case _:
            prime = ""

    return "$" + body + prime + "$"


def _op_latex(op: OperationLabel) -> str:
    """Return a LaTeX math-mode string for an OperationLabel, e.g. ``$C_{3}^{2}$``."""
    el = op.get_element()
    deg = op.get_degree()
    mul = op.get_multiple()

    deg_str = r"\infty" if deg == OperationLabel.DEGREE_INF else str(deg)

    match el:
        case OperationLabel.Element.ProperRotation:
            body = "C_{" + deg_str + "}"
            if mul != 1:
                body += "^{" + str(mul) + "}"
        case OperationLabel.Element.Inversion:
            body = "i"
        case OperationLabel.Element.ImproperRotation:
            body = "S_{" + deg_str + "}"
            if mul != 1:
                body += "^{" + str(mul) + "}"
        case OperationLabel.Element.Reflection:
            match op.get_plane():
                case OperationLabel.Plane.Horizontal:
                    body = r"\sigma_{h}"
                case OperationLabel.Plane.Vertical:
                    body = r"\sigma_{v}"
                case OperationLabel.Plane.Dihedral:
                    body = r"\sigma_{d}"
                case _:
                    body = r"\sigma"
        case _:
            raise RuntimeError(f"Unexpected element: {el}")

    match op.get_prime():
        case OperationLabel.Prime.Single:
            body += "'"
        case OperationLabel.Prime.Double:
            body += "''"

    return "$" + body + "$"


def _op_count_latex(olc: OperationLabelCount) -> str:
    """Return a LaTeX column header for an OperationLabelCount, e.g. ``$2C_{3}$``."""
    count = olc.get_count()
    label = olc.get_label()
    el = label.get_element()
    deg = label.get_degree()
    mul = label.get_multiple()

    deg_str = r"\infty" if deg == OperationLabel.DEGREE_INF else str(deg)

    match el:
        case OperationLabel.Element.ProperRotation:
            body = "C_{" + deg_str + "}"
            if mul != 1:
                body += "^{" + str(mul) + "}"
        case OperationLabel.Element.Inversion:
            body = "i"
        case OperationLabel.Element.ImproperRotation:
            body = "S_{" + deg_str + "}"
            if mul != 1:
                body += "^{" + str(mul) + "}"
        case OperationLabel.Element.Reflection:
            match label.get_plane():
                case OperationLabel.Plane.Horizontal:
                    body = r"\sigma_{h}"
                case OperationLabel.Plane.Vertical:
                    body = r"\sigma_{v}"
                case OperationLabel.Plane.Dihedral:
                    body = r"\sigma_{d}"
                case _:
                    body = r"\sigma"
        case _:
            raise RuntimeError(f"Unexpected element: {el}")

    match label.get_prime():
        case OperationLabel.Prime.Single:
            body += "'"
        case OperationLabel.Prime.Double:
            body += "''"

    # Infinite count (C∞v / D∞h)
    if count == OperationLabelCount.COUNT_INF:
        prefix = r"\infty "
    elif count > 1:
        prefix = str(count)
    else:
        prefix = ""

    return "$" + prefix + body + "$"


def _pg_label_latex(label: PointGroupLabel) -> str:
    """Return a LaTeX math-mode string for a PointGroupLabel, e.g. ``$C_{3v}$``."""
    name = label.get_name()
    # Map plain text name to LaTeX: subscript everything after the leading letter(s)
    # e.g. "C3v" → "C_{3v}", "D6h" → "D_{6h}", "Oh" → "O_{h}", "Td" → "T_{d}"
    # Strategy: split at the first digit or at a trailing letter suffix after an initial letter(s)
    import re
    m = re.match(r"^([A-Z]+)(.*)", name)
    if not m:
        return "$" + name + "$"
    leader, rest = m.group(1), m.group(2)
    # Replace ∞ with \infty
    rest = rest.replace("∞", r"\infty ")
    if rest:
        return "$" + leader + "_{" + rest + "}$"
    return "$" + leader + "$"


# ---------------------------------------------------------------------------
# Character value formatting
# ---------------------------------------------------------------------------

_EPS = 1e-9


def _fmt_char(val: float) -> str:
    """Format a character value: integer if close enough, else 4 d.p."""
    rounded = round(val)
    if abs(val - rounded) < _EPS:
        return str(int(rounded))
    return f"{val:.4f}"


# ---------------------------------------------------------------------------
# Single-table LaTeX builder
# ---------------------------------------------------------------------------

def _table_latex(pg: PointGroup) -> str:
    """Return the LaTeX for one character table (table + tabular environment)."""
    ops = pg.get_unique_operations()  # list[OperationLabelCount]
    irreps = pg.get_irreps()           # list[IrrepLabel]
    chars = pg.get_characters()        # list[list[float]]  [irrep][op]

    # unique_operations excludes the identity E; add it back as first column
    n_data_cols = 1 + len(ops)  # E + remaining operation classes
    col_spec = "l" + " r" * n_data_cols

    # Header row: group label, E, then remaining operation classes
    group_tex = _pg_label_latex(pg.get_label())
    op_headers = "$E$" + (" & " if ops else "") + " & ".join(_op_count_latex(o) for o in ops)
    header = group_tex + " & " + op_headers + r" \\"

    # Data rows
    data_rows: list[str] = []
    for i, ir in enumerate(irreps):
        row_chars = " & ".join(_fmt_char(v) for v in chars[i])
        data_rows.append("    " + _irrep_latex(ir) + " & " + row_chars + r" \\")

    caption = "Character table of " + _pg_label_latex(pg.get_label())

    lines = [
        r"\begin{table}[h]",
        r"  \centering",
        f"  \\caption{{{caption}}}",
        f"  \\begin{{tabular}}{{{col_spec}}}",
        r"    \toprule",
        "    " + header,
        r"    \midrule",
    ] + data_rows + [
        r"    \bottomrule",
        r"  \end{tabular}",
        r"\end{table}",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def format_latex(names: list[str]) -> str:
    """Return LaTeX code for one or more named point group character tables.

    The returned string contains bare table environments suitable for pasting
    into a LaTeX document that loads the ``booktabs`` and ``amsmath`` packages.
    For a standalone compilable document use :func:`save_latex`.
    """
    header = (
        "% Required packages: \\usepackage{booktabs} \\usepackage{amsmath}\n"
    )
    tables: list[str] = []
    for name in names:
        pg_label = parse_point_group_name(name)
        pg = get_or_generate_point_group(pg_label)
        if pg is None:
            raise ValueError(f"Unknown or unsupported point group: '{name}'")
        tables.append(_table_latex(pg))

    return header + "\n\n".join(tables)


def save_latex(names: list[str], path: str | None = None) -> Path:
    """Save a standalone LaTeX document with the requested character tables.

    Parameters
    ----------
    names:
        One or more Schoenflies group names, e.g. ``["C3v", "D6h"]``.
    path:
        Destination file path.  If *None*, an automatic name is generated
        from the group names, e.g. ``C3v_D6h_latex.tex``.

    Returns
    -------
    Path
        The path of the written file.
    """
    if path is None:
        stem = "_".join(n.replace("/", "-") for n in names)
        out_path = Path(stem + "_latex.tex")
    else:
        out_path = Path(path)

    tables: list[str] = []
    for name in names:
        pg_label = parse_point_group_name(name)
        pg = get_or_generate_point_group(pg_label)
        if pg is None:
            raise ValueError(f"Unknown or unsupported point group: '{name}'")
        tables.append(_table_latex(pg))

    body = "\n\n".join(tables)

    doc = "\n".join([
        r"\documentclass{article}",
        r"\usepackage{booktabs}",
        r"\usepackage{amsmath}",
        r"\begin{document}",
        "",
        body,
        "",
        r"\end{document}",
    ])

    out_path.write_text(doc, encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m pyrrhotite.character_tables.latex_formatter",
        description=(
            "Print or save LaTeX character tables for Schoenflies point groups. "
            "Requires LaTeX packages: booktabs, amsmath."
        ),
    )
    p.add_argument(
        "groups",
        nargs="+",
        metavar="GROUP",
        help="One or more point group names, e.g. C3v D6h Oh",
    )
    p.add_argument(
        "--save",
        nargs="?",
        const=True,   # flag present but no filename → auto-name
        default=False,
        metavar="FILE",
        help=(
            "Save to FILE as a standalone LaTeX document. "
            "Omit FILE to auto-generate the filename."
        ),
    )
    return p


def main(argv: list[str] | None = None) -> int:
    """Entry point for CLI use."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.save is False:
            # Print bare table(s) to stdout
            print(format_latex(args.groups))
        else:
            file_arg = None if args.save is True else args.save
            out = save_latex(args.groups, file_arg)
            print(f"Saved to {out}", file=sys.stderr)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
