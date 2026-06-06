"""
example_usage.py — Complete showcase of the pyrrhotite package.

Sections
--------
 1.  Structure loading & atom list
 2.  Point group determination
 3.  Rotor classification & principal axes
 4.  Symmetry operations
 5.  Character table display
 6.  Basis function assignment
 7.  Programmatic character table access
 8.  Standalone character table generator (no XYZ needed)
 9.  LaTeX formatter
10.  HTML formatter
11.  Multi-group export (LaTeX + HTML)
12.  Periodic table utilities

Run:
    python example_usage.py
"""

import sys
import io

# Unicode fix for Windows terminals (σ, ε, ′, ″, ∞, …)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-16"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from pyrrhotite import Structure, Symmetry
from pyrrhotite.periodic_table import get_element, get_atomic_number
from pyrrhotite.operations.operation_label import OperationLabel
from pyrrhotite.point_groups.basis_functions import compute_basis_functions
from pyrrhotite.character_tables import (
    generate_point_group,
    get_or_generate_point_group,
    parse_point_group_name,
    print_character_table_for,
    format_latex,
    save_latex,
    format_html,
    save_html,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SEP  = "=" * 60
SEP2 = "-" * 60

def section(n: int, title: str) -> None:
    print()
    print(SEP)
    print(f"{n}. {title}")
    print(SEP)

# ---------------------------------------------------------------------------
# 1. Structure loading & atom list
# ---------------------------------------------------------------------------

section(1, "STRUCTURE LOADING & ATOM LIST")

s = Structure(r"tests\files\ammonia.xyz")

print(f"File        : {s.filename}")
print(f"Description : {s.description}")
print(f"Num atoms   : {s.num_atoms}")
print(f"Coordinates shape : {s.coordinates.shape}   (N × 3, Å)")
print(f"Atomic numbers    : {s.atomic_numbers.tolist()}")

print()
print("Bond pairs (connectivity):")
for a, b in s.calculate_bond_pairs():
    ea = get_element(int(s.atomic_numbers[a])).symbol
    eb = get_element(int(s.atomic_numbers[b])).symbol
    print(f"  {ea}{a} — {eb}{b}")

print()
print("Atom list (COM-centred coordinates):")
s.print_atom_list()

# ---------------------------------------------------------------------------
# 2. Point group determination
# ---------------------------------------------------------------------------

section(2, "POINT GROUP DETERMINATION")

sym = Symmetry(s)
pg  = sym.get_point_group()
mgr = sym.get_operation_manager()

print(f"Point group : {pg.get_label().get_name()}")
print(f"Group order : {pg.get_order()}   (total symmetry operations)")

# Show a second molecule for comparison
s_bz  = Structure(r"tests\files\benzene.xyz")
sym_bz = Symmetry(s_bz)
pg_bz  = sym_bz.get_point_group()
print()
print(f"Benzene     : {pg_bz.get_label().get_name()}  (order {pg_bz.get_order()})")

# ---------------------------------------------------------------------------
# 3. Rotor classification & principal axes
# ---------------------------------------------------------------------------

section(3, "ROTOR CLASSIFICATION & PRINCIPAL AXES")

rc = sym.get_rotor_class()
print(f"Rotor class : {rc.name}")

pm = sym.get_principal_moments()
print(f"\nPrincipal moments of inertia (u·Å²):")
print(f"  Ia = {pm[0]:.6f}")
print(f"  Ib = {pm[1]:.6f}")
print(f"  Ic = {pm[2]:.6f}")

axes = sym.get_principal_axes()
print(f"\nPrincipal axes (columns = eigenvectors along x, y, z):")
print(f"  {'':6}  {'x':>12}  {'y':>12}  {'z':>12}")
for i, row_label in enumerate(["x", "y", "z"]):
    vals = "  ".join(f"{axes[i, col]:12.6f}" for col in range(3))
    print(f"  {row_label:<6}  {vals}")

print(f"\nCartesian x-axis : {sym.get_x_axis().round(4).tolist()}")
print(f"Cartesian y-axis : {sym.get_y_axis().round(4).tolist()}")
print(f"Cartesian z-axis : {sym.get_z_axis().round(4).tolist()}")

print("\nFull Cartesian axes matrix:")
print(sym.get_cartesian_axes())

# ---------------------------------------------------------------------------
# 4. Symmetry operations
# ---------------------------------------------------------------------------

section(4, "SYMMETRY OPERATIONS")

print("All found operations:")
for op in mgr.get_operations():
    print(f"  {op.get_label().get_short_name():<10}  "
          f"axis={op.get_axis().round(3).tolist()}  "
          f"error={op.get_error():.4f} Å")

print()
print("Filtered by type:")
print("  Proper rotations  :", [o.get_label().get_short_name() for o in mgr.get_proper_rotations()])
print("  Improper rotations:", [o.get_label().get_short_name() for o in mgr.get_improper_rotations()])
print("  Reflections       :", [o.get_label().get_short_name() for o in mgr.get_reflections()])
print("  Inversions        :", [o.get_label().get_short_name() for o in mgr.get_inversions()])

print()
print("Atoms on each symmetry element:")
for op in mgr.get_operations():
    label = op.get_label()
    short = label.get_short_name()
    if label.get_element() == OperationLabel.Element.Reflection:
        atom_indices = op.get_atoms_in_plane(s)
        location = "in plane"
        if op.is_molecular_plane(s):
            location += " [molecular plane]"
    else:
        atom_indices = op.get_atoms_on_axis(s)
        location = "on axis"
    atom_str = ", ".join(
        f"{get_element(int(s.atomic_numbers[i])).symbol}{i}" for i in atom_indices
    ) or "none"
    print(f"  {short:<10}  {location}: {atom_str}")

print()
print("Operation summary (by type):")
summary = mgr.summarize()
for op_type, ops_list in summary.items():
    print(f"  {op_type:<22}: {[o.get_label().get_short_name() for o in ops_list]}")

# ---------------------------------------------------------------------------
# 5. Character table display
# ---------------------------------------------------------------------------

section(5, "CHARACTER TABLE DISPLAY")

print("-- Default (rich formatting with basis functions) --")
pg.print_character_table()

print()
print("-- Plain-text renderer --")
pg.print_character_table(plain=True)

print()
print("-- Complex (ε) notation for a cyclic group C6 --")
pg_c6 = get_or_generate_point_group(parse_point_group_name("C6"))
pg_c6.print_character_table(complex=True)

# ---------------------------------------------------------------------------
# 6. Basis function assignment
# ---------------------------------------------------------------------------

section(6, "BASIS FUNCTION ASSIGNMENT")

bf = compute_basis_functions(pg)
print(f"  {'Irrep':<8}  {'Linear / Rotational':<26}  Quadratic")
print("  " + SEP2)
for irrep_name, funcs in bf.items():
    lin  = ", ".join(funcs["linear"])    or "—"
    quad = ", ".join(funcs["quadratic"]) or "—"
    print(f"  {irrep_name:<8}  {lin:<26}  {quad}")

# ---------------------------------------------------------------------------
# 7. Programmatic character table access
# ---------------------------------------------------------------------------

section(7, "PROGRAMMATIC CHARACTER TABLE ACCESS")

irreps  = pg.get_irreps()
ops     = pg.get_unique_operations()
chars   = pg.get_characters()

print("Irreducible representations:")
for ir in irreps:
    print(f"  {ir.get_name()}")

print("\nConjugacy classes (from unique_operations, excluding E):")
for olc in ops:
    print(f"  {olc.get_short_name():<12}  count={olc.get_count()}")

print("\nFull character table (rows = irreps, columns = E then unique ops):")
header = f"  {'':>6}" + "".join(f"  {'E':>6}") + "".join(f"  {o.get_label().get_short_name():>6}" for o in ops)
print(header)
for i, ir in enumerate(irreps):
    row = "  ".join(f"{v:6.3f}" for v in chars[i])
    print(f"  {ir.get_name():<6}  {row}")

# ---------------------------------------------------------------------------
# 8. Standalone character table generator (no XYZ needed)
# ---------------------------------------------------------------------------

section(8, "STANDALONE CHARACTER TABLE GENERATOR  (no XYZ needed)")

print("-- parse_point_group_name + get_or_generate_point_group --")
label_d6h = parse_point_group_name("D6h")
pg_d6h    = get_or_generate_point_group(label_d6h)
print(f"D6h  order={pg_d6h.get_order()}  irreps={len(pg_d6h.get_irreps())}")

print()
print("-- generate_point_group (always regenerates, bypasses cache) --")
pg_d4d = generate_point_group(parse_point_group_name("D4d"))
print(f"D4d  order={pg_d4d.get_order()}  irreps={len(pg_d4d.get_irreps())}")

print()
print("-- print_character_table_for (one-liner display) --")
print_character_table_for("C3v")

print()
print("-- D6h (dihedral, g/u splitting) --")
print_character_table_for("D6h")

print()
print("-- D4d (antiprismatic) --")
print_character_table_for("D4d")

print()
print("-- C24 (high-order generated group, plain to avoid truncation) --")
pg_c24 = get_or_generate_point_group(parse_point_group_name("C24"))
pg_c24.print_character_table(plain=True)

# ---------------------------------------------------------------------------
# 9. LaTeX formatter
# ---------------------------------------------------------------------------

section(9, "LATEX FORMATTER")

print("-- format_latex: inline, print to stdout --")
latex_code = format_latex(["C3v", "D6h"])
print(latex_code)

print()
print("-- save_latex: write a standalone .tex document --")
tex_path = save_latex(["Oh"], "oh_table.tex")
print(f"Saved to: {tex_path}")
print("File contents:")
print(tex_path.read_text(encoding="utf-8"))

# ---------------------------------------------------------------------------
# 10. HTML formatter
# ---------------------------------------------------------------------------

section(10, "HTML FORMATTER")

print("-- format_html: inline, print to stdout (first 800 chars) --")
html_fragment = format_html(["C3v"])
print(html_fragment[:800])
print("  ... [truncated]")

print()
print("-- save_html: write a standalone .html document --")
html_path = save_html(["D6h"], "d6h_table.html")
print(f"Saved to: {html_path}")
print(f"File size: {html_path.stat().st_size} bytes")

# ---------------------------------------------------------------------------
# 11. Multi-group export
# ---------------------------------------------------------------------------

section(11, "MULTI-GROUP EXPORT (LaTeX + HTML)")

groups = ["C2v", "C3v", "C4v"]

multi_tex  = save_latex(groups)        # auto-named C2v_C3v_C4v_latex.tex
multi_html = save_html(groups)         # auto-named C2v_C3v_C4v_html.html
print(f"LaTeX saved to : {multi_tex}   ({multi_tex.stat().st_size} bytes)")
print(f"HTML  saved to : {multi_html}  ({multi_html.stat().st_size} bytes)")

# Show that format_latex returns all three tables in one string
combined = format_latex(groups)
table_count = combined.count(r"\begin{table}")
print(f"format_latex(['C2v','C3v','C4v']) contains {table_count} \\begin{{table}} environments.")

# ---------------------------------------------------------------------------
# 12. Periodic table utilities
# ---------------------------------------------------------------------------

section(12, "PERIODIC TABLE UTILITIES")

el = get_element(6)
print(f"Element 6  : symbol={el.symbol}, name={el.name}, mass={el.mass} u, "
      f"radius={el.radius} Å, colour={el.colour}")

n_fe = get_atomic_number("Fe")
fe   = get_element(n_fe)
print(f"Iron       : atomic number={n_fe}, mass={fe.mass} u")

print()
print("Atoms in ammonia molecule:")
for i, z in enumerate(s.atomic_numbers):
    el_i = get_element(int(z))
    print(f"  Atom {i}: Z={int(z):3d}  symbol={el_i.symbol:<3}  mass={el_i.mass:.4f} u")

print()
print("Done. All sections completed successfully.")
print()
print("Cleaning up generated files:")
for p in [tex_path, html_path, multi_tex, multi_html]:
    p.unlink(missing_ok=True)
    print(f"  Removed {p}")
