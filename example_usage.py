import sys, io

# Ensure Unicode output works on Windows terminals (σ, ′, ″, ε, …)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-16"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from schoenflies import Structure, Symmetry
from schoenflies.periodic_table import get_element, get_atomic_number
from schoenflies.operations.operation_label import OperationLabel
from schoenflies.point_groups.basis_functions import compute_basis_functions
from schoenflies.point_groups.character_table_generator import (
    parse_point_group_name,
    get_or_generate_point_group,
    print_character_table_for,
)

SEP = "=" * 60

# ── Load structure ─────────────────────────────────────────────────────────────
s = Structure("tests\\files\\ammonia.xyz")
sym = Symmetry(s)
pg = sym.get_point_group()
mgr = sym.get_operation_manager()

print(SEP)
print("1. POINT GROUP DETERMINATION")
print(SEP)

print("Point group :", pg.get_label().get_name())   # "C3v"
print("Group order :", pg.get_order())               # total number of operations

# ── Rotor classification and principal axes ────────────────────────────────────
print()
print(SEP)
print("2. ROTOR CLASSIFICATION AND PRINCIPAL AXES")
print(SEP)

print("Rotor class :", sym.get_rotor_class())        # RotorClass.ProlateSymmetricTop

pm = sym.get_principal_moments()
print(f"\nPrincipal moments of inertia (u·Å²):")
print(f"  Ia = {pm[0]:.6f}")
print(f"  Ib = {pm[1]:.6f}")
print(f"  Ic = {pm[2]:.6f}")

axes = sym.get_principal_axes()
print(f"\nPrincipal axes (columns = x, y, z eigenvectors):")
print(f"  {'':6}  {'x':>12}  {'y':>12}  {'z':>12}")
for i, row in enumerate(["x", "y", "z"]):
    vals = "  ".join(f"{axes[i, col]:12.6f}" for col in range(3))
    print(f"  {row:6}  {vals}")

print("\nCartesian axes matrix (conventional frame):")
print(sym.get_cartesian_axes())

# ── Symmetry operations ────────────────────────────────────────────────────────
print()
print(SEP)
print("3. SYMMETRY OPERATIONS")
print(SEP)

print("All found operations:")
for op in mgr.get_operations():
    print(f"  {op.get_label().get_short_name():<10}  axis={op.get_axis().round(3).tolist()}"
          f"  error={op.get_error():.4f} Å")

print("\nFiltered by type:")
print("  Proper rotations :", [o.get_label().get_short_name() for o in mgr.get_proper_rotations()])
print("  Improper rotations:", [o.get_label().get_short_name() for o in mgr.get_improper_rotations()])
print("  Reflections      :", [o.get_label().get_short_name() for o in mgr.get_reflections()])
print("  Inversions       :", [o.get_label().get_short_name() for o in mgr.get_inversions()])

print("\nAtoms on each symmetry element:")
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
        f"{get_element(s.atomic_numbers[i]).symbol}{i}" for i in atom_indices
    ) or "none"
    print(f"  {short:<10}  {location}: {atom_str}")

# ── Character table ────────────────────────────────────────────────────────────
print()
print(SEP)
print("4. CHARACTER TABLE")
print(SEP)

print("\n-- Default (rich formatting with basis functions) --")
pg.print_character_table()

print("\n-- Plain-text renderer --")
pg.print_character_table(plain=True)

print("\n-- Programmatic access to table data --")
print("Irreps:", [irr.get_name() for irr in pg.get_irreps()])
print("Conjugacy classes:", [op.get_short_name() for op in pg.get_unique_operations()])
print("Characters (row 0):", pg.get_characters()[0])

# ── Basis functions ────────────────────────────────────────────────────────────
print()
print(SEP)
print("5. BASIS FUNCTION ASSIGNMENT")
print(SEP)

bf = compute_basis_functions(pg)
print(f"{'Irrep':<8}  {'Linear / Rotational':<24}  Quadratic")
for irrep_name, funcs in bf.items():
    lin  = ", ".join(funcs["linear"])    or "—"
    quad = ", ".join(funcs["quadratic"]) or "—"
    print(f"  {irrep_name:<6}  {lin:<24}  {quad}")

# ── Character table generator ──────────────────────────────────────────────────
print()
print(SEP)
print("6. CHARACTER TABLE GENERATOR  (no XYZ needed)")
print(SEP)

print("\n-- C3v: print directly by name --")
print_character_table_for("C3v")

print("\n-- C6: complex (ε) notation for cyclic groups --")
label = parse_point_group_name("C6")
pg_c6 = get_or_generate_point_group(label)
pg_c6.print_character_table(complex=True)

print("\n-- D6h: dihedral group with g/u splitting --")
print_character_table_for("D6h")

print("\n-- D4d: antiprismatic group --")
print_character_table_for("D4d")

print("\n-- C24: high-order generated group (plain to avoid truncation) --")
label = parse_point_group_name("C24")
pg_c24 = get_or_generate_point_group(label)
pg_c24.print_character_table(plain=True)

# ── Element data ───────────────────────────────────────────────────────────────
print()
print(SEP)
print("7. ELEMENT DATA")
print(SEP)

el = get_element(6)
print(f"Element 6  : symbol={el.symbol}, name={el.name}, mass={el.mass}, "
      f"radius={el.radius} Å, colour={el.colour}")

n = get_atomic_number("Fe")
fe = get_element(n)
print(f"Iron       : atomic number={n}, mass={fe.mass}")

# ── Atom list ──────────────────────────────────────────────────────────────────
print()
print(SEP)
print("8. ATOM LIST (COM-centred coordinates)")
print(SEP)
s.print_atom_list()
