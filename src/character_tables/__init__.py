"""
Character table generation, lookup, and export.

`generator.py` builds character tables for any of the 18 Schoenflies point-group
classes — analytically for the seven axial families (Cn, Cnh, Cnv, Sn, Dn, Dnh,
Dnd) at any order, and from a built-in table for the rest. `html_formatter.py` and
`latex_formatter.py` turn the resulting PointGroup objects into ready-to-use HTML
or LaTeX tables.
"""

from .generator import (
    generate_point_group,
    find_point_group,
    get_or_generate_point_group,
    parse_point_group_name,
    print_character_table_for,
)
from .html_formatter import format_html, save_html
from .latex_formatter import format_latex, save_latex

__all__ = [
    "generate_point_group",
    "find_point_group",
    "get_or_generate_point_group",
    "parse_point_group_name",
    "print_character_table_for",
    "format_latex",
    "save_latex",
    "format_html",
    "save_html",
]
