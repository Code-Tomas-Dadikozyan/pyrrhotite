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
13.  3-D visualizer
14.  Idealized structure generator

This is the canonical "what can pyrrhotite do?" tour — every public feature is
exercised once, with comments explaining what each call returns. It reads its
molecules from the bundled sample set (via `load_sample`), so it runs as-is
straight after `pip install pyrrhotite`, with no `.xyz` files of your own.

Run:
    python example_usage.py

Sections 13 and 14 open the interactive 3-D viewer; they are skipped
automatically unless the optional viewer extras are installed
(`pip install 'pyrrhotite[vis]'`).
"""

import sys
import io
from pathlib import Path

# Unicode fix for Windows terminals (σ, ε, ′, ″, ∞, …)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-16"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from pyrrhotite import (
    Structure,
    Symmetry,
    load_sample,
    generate_idealized_structure,
    write_xyz,
    visualize_idealized_structure,
)
from pyrrhotite.structure_generator import format_xyz
from pyrrhotite.periodic_table import element, atomic_number
from pyrrhotite.display import (
    print_bond_pairs,
    print_ops_with_atoms,
    print_basis_functions,
    print_char_table_programmatic,
)
from pyrrhotite.character_tables import (
    generate_point_group,
    find_point_group,
    print_character_table_for,
    format_latex,
    save_latex,
    format_html,
    save_html,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SEP = "=" * 60

def section(n: int, title: str) -> None:
    print()
    print(SEP)
    print(f"{n}. {title}")
    print(SEP)



# ---------------------------------------------------------------------------
# 1. Structure loading & atom list
# ---------------------------------------------------------------------------

section(1, "STRUCTURE LOADING & ATOM LIST")

# We use the bundled sample molecules (load_sample) so this script runs
# anywhere — including a plain `pip install pyrrhotite` with no source checkout.
# To analyse your own molecule instead, replace this with:
#     s = Structure("path/to/your_molecule.xyz")
s = load_sample("ammonia")

print(f"File        : {s.filename}")
print(f"Description : {s.description}")
print(f"Num atoms   : {s.num_atoms}")
print(f"Coordinates shape : {s.coordinates.shape}   (N × 3, Å)")
print(f"Atomic numbers    : {s.atomic_numbers.tolist()}")

print()
print("Bond pairs (connectivity):")
print_bond_pairs(s)

print()
print("Atom list (COM-centred coordinates):")
s.print_atom_list()

# ---------------------------------------------------------------------------
# 2. Point group determination
# ---------------------------------------------------------------------------

section(2, "POINT GROUP DETERMINATION")

sym = Symmetry(s)
pg  = sym.point_group
mgr = sym.operation_manager

print(f"Point group : {pg.label.name}")
print(f"Group order : {pg.order}   (total symmetry operations)")

# Show a second molecule for comparison
s_bz   = load_sample("benzene")
sym_bz = Symmetry(s_bz)
pg_bz  = sym_bz.point_group
print()
print(f"Benzene     : {pg_bz.label.name}  (order {pg_bz.order})")

# ---------------------------------------------------------------------------
# 3. Rotor classification & principal axes
# ---------------------------------------------------------------------------

section(3, "ROTOR CLASSIFICATION & PRINCIPAL AXES")

rc = sym.rotor_class
print(f"Rotor class : {rc.name}")

pm = sym.principal_moments
print(f"\nPrincipal moments of inertia (u·Å²):")
print(f"  Ia = {pm[0]:.6f}")
print(f"  Ib = {pm[1]:.6f}")
print(f"  Ic = {pm[2]:.6f}")

axes = sym.principal_axes
print(f"\nPrincipal axes (columns = eigenvectors along x, y, z):")
print(f"  {'':6}  {'x':>12}  {'y':>12}  {'z':>12}")
for i, row_label in enumerate(["x", "y", "z"]):
    vals = "  ".join(f"{axes[i, col]:12.6f}" for col in range(3))
    print(f"  {row_label:<6}  {vals}")

print(f"\nCartesian x-axis : {sym.x_axis.round(4).tolist()}")
print(f"Cartesian y-axis : {sym.y_axis.round(4).tolist()}")
print(f"Cartesian z-axis : {sym.z_axis.round(4).tolist()}")

print("\nFull Cartesian axes matrix:")
print(sym.cartesian_axes)

# ---------------------------------------------------------------------------
# 4. Symmetry operations
# ---------------------------------------------------------------------------

section(4, "SYMMETRY OPERATIONS")

print("All found operations:")
for op in mgr.operations:
    print(f"  {op.label.short_name:<10}  "
          f"axis={op.axis.round(3).tolist()}  "
          f"error={op.error:.4f} Å")

print()
print("Filtered by type:")
print("  Proper rotations  :", [o.label.short_name for o in mgr.proper_rotations])
print("  Improper rotations:", [o.label.short_name for o in mgr.improper_rotations])
print("  Reflections       :", [o.label.short_name for o in mgr.reflections])
print("  Inversions        :", [o.label.short_name for o in mgr.inversions])

print()
print("Atoms on each symmetry element:")
print_ops_with_atoms(mgr.operations, s)

print()
print("Operation summary (by type):")
summary = mgr.summarize()
for op_type, ops_list in summary.items():
    print(f"  {op_type:<22}: {[o.label.short_name for o in ops_list]}")

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
pg_c6 = find_point_group("C6")
pg_c6.print_character_table(complex=True)

# ---------------------------------------------------------------------------
# 6. Basis function assignment
# ---------------------------------------------------------------------------

section(6, "BASIS FUNCTION ASSIGNMENT")
print_basis_functions(pg)

# ---------------------------------------------------------------------------
# 7. Programmatic character table access
# ---------------------------------------------------------------------------

section(7, "PROGRAMMATIC CHARACTER TABLE ACCESS")
print_char_table_programmatic(pg)

# ---------------------------------------------------------------------------
# 8. Standalone character table generator (no XYZ needed)
# ---------------------------------------------------------------------------

section(8, "STANDALONE CHARACTER TABLE GENERATOR  (no XYZ needed)")

print("-- find_point_group (accepts a Schoenflies name string) --")
pg_d6h = find_point_group("D6h")
print(f"D6h  order={pg_d6h.order}  irreps={len(pg_d6h.irreps)}")

print()
print("-- generate_point_group (always regenerates, bypasses cache) --")
pg_d4d = generate_point_group("D4d")
print(f"D4d  order={pg_d4d.order}  irreps={len(pg_d4d.irreps)}")

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
pg_c24 = find_point_group("C24")
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

el = element(6)
print(f"Element 6  : symbol={el.symbol}, name={el.name}, mass={el.mass} u, "
      f"radius={el.radius} Å, colour={el.colour}")

n_fe = atomic_number("Fe")
fe   = element(n_fe)
print(f"Iron       : atomic number={n_fe}, mass={fe.mass} u")

print()
print("Atoms in ammonia molecule:")
for i, z in enumerate(s.atomic_numbers):
    el_i = element(int(z))
    print(f"  Atom {i}: Z={int(z):3d}  symbol={el_i.symbol:<3}  mass={el_i.mass:.4f} u")

print()
print("Done. All sections completed successfully.")
print()
print("Cleaning up generated files:")
for p in [tex_path, html_path, multi_tex, multi_html]:
    p.unlink(missing_ok=True)
    print(f"  Removed {p}")

# ---------------------------------------------------------------------------
# 13. 3-D visualizer
# ---------------------------------------------------------------------------

section(13, "3-D VISUALIZER")

print("The visualizer requires optional dependencies:")
print("  pip install 'pyrrhotite[vis]'   (PyQt6, PyOpenGL, pyrr)")
print()
print("Python API:")
print("  from pyrrhotite import Structure, visualize")
print("  visualize(Structure('molecule.xyz'))")
print()
print("CLI:")
print("  pyrrhotite molecule.xyz --visualize")
print()

try:
    import PyQt6       # pip install PyQt6
    import OpenGL      # pip install PyOpenGL  (note: package name differs from import name)
    import pyrr        # pip install pyrr
    deps_ok = True
except ImportError as e:
    deps_ok = False
    print(f"Optional vis dependencies not installed ({e}); skipping live demo.")
    print("Install with:  pip install PyQt6 PyOpenGL pyrr")
    print("           or: pip install 'pyrrhotite[vis]'")

if deps_ok:
    print("Visualizer dependencies found — opening window for ammonia (NH₃).")
    print("Controls: left-drag to rotate | scroll to zoom | close window to continue.")
    print()
    from pyrrhotite import visualize
    visualize(s)   # s = ammonia, loaded in section 1

# ---------------------------------------------------------------------------
# 14. Idealized structure generator
# ---------------------------------------------------------------------------

section(14, "IDEALIZED STRUCTURE GENERATOR")

print("generate_idealized_structure(name) builds a synthetic Structure whose")
print("geometry has, by construction, the requested axial point group symmetry")
print("(Cn, Cnh, Cnv, Sn, Dn, Dnh, Dnd). Useful as test fixtures and for exploring")
print("how the symmetry-detection pipeline behaves at a chosen order n.")

# Step 1: generate_idealized_structure(name) takes a Schoenflies name (e.g.
# "D6h", "C5v", "S8") and returns an in-memory Structure with that point
# group symmetry, by construction. No XYZ file is read or written here.
print()
print("-- Basic generation + round-trip through Symmetry --")
s_d6h = generate_idealized_structure("D6h")
print(f"Description : {s_d6h.description}")
print(f"Num atoms   : {s_d6h.num_atoms}")
print(f"Detected    : {Symmetry(s_d6h).point_group.label.name}")

# Step 2: to get XYZ-formatted text without writing a file (e.g. to stream,
# pipe, or inspect), pass the Structure to format_xyz().
print()
print("-- format_xyz: get the structure as XYZ text without touching disk --")
xyz_text = format_xyz(generate_idealized_structure("C5v"))
print(xyz_text)

# Step 3: to produce an actual .xyz file on disk, pass the Structure and a
# path to write_xyz(structure, path). The resulting file can be reloaded
# with Structure(path) just like any other XYZ file (e.g. for Symmetry()
# analysis, the CLI, or the visualizer).
print()
print("-- write_xyz: save to disk, then reload and re-analyse --")
gen_path = Path("c10v_generated.xyz")
write_xyz(generate_idealized_structure("C10v"), gen_path)
reloaded = Structure(str(gen_path))
print(f"Saved {gen_path} ({reloaded.num_atoms} atoms)")
print(f"Re-detected point group: {Symmetry(reloaded).point_group.label.name}")
gen_path.unlink(missing_ok=True)
print(f"Removed {gen_path}")

print()
print("-- Round trip across all seven axial families (n=6) --")
for name in ["C6", "C6h", "C6v", "S6", "D6", "D6h", "D6d"]:
    structure = generate_idealized_structure(name)
    detected = Symmetry(structure).point_group.label.name
    match = "OK" if detected == name else f"MISMATCH (got {detected})"
    print(f"  {name:<5} -> {detected:<5} {match}")

print()
print("-- Customising radius / height / element --")
s_custom = generate_idealized_structure("D5h", radius=2.0, height=1.5, element="Cl")
print(f"Description : {s_custom.description}")
print(f"Detected    : {Symmetry(s_custom).point_group.label.name}")

print()
print("-- Errors for unsupported inputs --")
for bad_name in ["Td", "S5", "C2"]:
    try:
        generate_idealized_structure(bad_name)
    except ValueError as exc:
        print(f"  {bad_name}: ValueError: {exc}")

# Step 4: visualize_idealized_structure(name) generates the structure and
# opens it directly in the 3-D viewer -- no call to write_xyz/Structure()
# needed. It requires the optional [vis] dependencies (PyQt6, PyOpenGL, pyrr),
# checked above in section 13 via `deps_ok`.
print()
print("-- visualize_idealized_structure: preview without saving an XYZ file --")
if deps_ok:
    print("Opening viewer for a generated D9d structure (note the ferrocene-style")
    print("layout: a central hub atom connects the two 9-rings, and each ring atom")
    print("has a realistic bond count -- close the window to continue).")
    visualize_idealized_structure("D9d")
    visualize_idealized_structure("D9d", show_labels=True)
else:
    print("Optional vis dependencies not installed; skipping live demo.")
    print('Install with:  pip install \'pyrrhotite[vis]\'')

# The CLI exposes the same generator via -g/--group + --xyz / --visualize,
# without needing any Python code:
#   pyrrhotite -g <NAME> --xyz            print the generated structure as XYZ
#                                          to stdout (e.g. to pipe elsewhere)
#   pyrrhotite -g <NAME> --xyz PATH       write the generated structure as XYZ
#                                          to PATH instead of stdout
#   pyrrhotite -g <NAME> --visualize      open the 3-D viewer for the
#                                          generated structure directly
#   pyrrhotite PATH -v                    analyse a generated (or any other)
#                                          XYZ file as usual
print()
print("CLI equivalents:")
print("  pyrrhotite -g C12v --xyz                  # print generated XYZ to stdout")
print("  pyrrhotite -g D9d --xyz d9d.xyz           # save generated XYZ to a file")
print("  pyrrhotite -g D9d --visualize             # preview the generated structure")
print("  pyrrhotite d9d.xyz -v                     # then analyse it as usual")
