"""
HTML formatter for Schoenflies point group character tables.

Inline API
----------
    from pyrrhotite.character_tables import format_html, save_html

    print(format_html(["C3v", "D6h"]))
    path = save_html(["Oh"], "oh_table.html")

CLI
---
    python -m pyrrhotite.character_tables.html_formatter C3v D6h
    python -m pyrrhotite.character_tables.html_formatter Oh --save
    python -m pyrrhotite.character_tables.html_formatter Oh D4h --save tables.html
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..point_groups.point_group import PointGroup
from .generator import get_or_generate_point_group

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

_CSS = """\
<style>
  .char-table {
    border-collapse: collapse;
    font-family: "Latin Modern", "STIX Two Text", serif;
    font-size: 0.95em;
    margin: 1.5em auto;
  }
  .char-table caption {
    caption-side: top;
    font-weight: bold;
    margin-bottom: 0.4em;
  }
  .char-table th,
  .char-table td {
    padding: 0.35em 0.75em;
    text-align: center;
    border: 1px solid #bbb;
  }
  .char-table thead tr {
    background: #e8e8e8;
    border-bottom: 2px solid #555;
  }
  .char-table thead th:first-child {
    text-align: left;
  }
  .char-table tbody td:first-child {
    text-align: left;
    font-style: normal;
  }
  .char-table tbody tr:nth-child(even) {
    background: #f5f5f5;
  }
  .char-table tbody tr:hover {
    background: #e0ecf8;
  }
</style>"""

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
# Single-table HTML builder
# ---------------------------------------------------------------------------

def _table_html(pg: PointGroup) -> str:
    """Return an HTML ``<table>`` element for one character table."""
    ops = pg.unique_operations  # list[OperationLabelCount]
    irreps = pg.irreps           # list[IrrepLabel]
    chars = pg.characters        # list[list[float]]

    group_html = pg.label.name_html
    caption = f"Character table of {group_html}"

    # Header cells — unique_operations excludes E; prepend it explicitly
    op_headers = "      <th><i>E</i></th>\n" + "".join(
        f"      <th>{o.short_name_html}</th>\n" for o in ops
    )
    header_row = (
        f"    <tr>\n"
        f"      <th>{group_html}</th>\n"
        f"{op_headers}"
        f"    </tr>"
    )

    # Data rows
    rows: list[str] = []
    for i, ir in enumerate(irreps):
        cells = "".join(
            f"      <td>{_fmt_char(v)}</td>\n" for v in chars[i]
        )
        rows.append(
            f"    <tr>\n"
            f"      <td>{ir.name_html}</td>\n"
            f"{cells}"
            f"    </tr>"
        )

    tbody = "\n".join(rows)

    return (
        f'<table class="char-table">\n'
        f"  <caption>{caption}</caption>\n"
        f"  <thead>\n{header_row}\n  </thead>\n"
        f"  <tbody>\n{tbody}\n  </tbody>\n"
        f"</table>"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def format_html(names: list[str]) -> str:
    """Return HTML code for one or more named point group character tables.

    The returned string is a ``<style>`` block followed by one ``<table>``
    per group — suitable for embedding in an existing HTML page.  For a
    complete standalone document use :func:`save_html`.
    """
    tables: list[str] = []
    for name in names:
        pg = get_or_generate_point_group(name)
        if pg is None:
            raise ValueError(f"Unknown or unsupported point group: '{name}'")
        tables.append(_table_html(pg))

    return _CSS + "\n\n" + "\n\n".join(tables)


def save_html(names: list[str], path: str | None = None) -> Path:
    """Save a standalone HTML document with the requested character tables.

    Parameters
    ----------
    names:
        One or more Schoenflies group names, e.g. ``["C3v", "D6h"]``.
    path:
        Destination file path.  If *None*, an automatic name is generated
        from the group names, e.g. ``C3v_D6h_html.html``.

    Returns
    -------
    Path
        The path of the written file.
    """
    if path is None:
        stem = "_".join(n.replace("/", "-") for n in names)
        out_path = Path(stem + "_html.html")
    else:
        out_path = Path(path)

    tables: list[str] = []
    titles: list[str] = []
    for name in names:
        pg = get_or_generate_point_group(name)
        if pg is None:
            raise ValueError(f"Unknown or unsupported point group: '{name}'")
        tables.append(_table_html(pg))
        titles.append(pg.label.name)

    page_title = "Character Tables — " + ", ".join(titles)
    tables_html = "\n\n".join(tables)

    doc = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title}</title>
{_CSS}
</head>
<body>
  <h1>{page_title}</h1>

{tables_html}

</body>
</html>
"""

    out_path.write_text(doc, encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    """Build the argparse parser for the HTML-formatter command-line entry point."""
    p = argparse.ArgumentParser(
        prog="python -m pyrrhotite.character_tables.html_formatter",
        description="Print or save HTML character tables for Schoenflies point groups.",
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
        const=True,
        default=False,
        metavar="FILE",
        help=(
            "Save to FILE as a standalone HTML document. "
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
            print(format_html(args.groups))
        else:
            file_arg = None if args.save is True else args.save
            out = save_html(args.groups, file_arg)
            print(f"Saved to {out}", file=sys.stderr)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
