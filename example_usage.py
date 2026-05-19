import sys, io
# ensure Unicode output works on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-16"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from schoenflies import Structure, Symmetry

# s = Structure("tests\\files\\methane.xyz")
# sym = Symmetry(s)
# mgr = sym.get_operation_manager()

# # ── Point group ────────────────────────────────────────────────────────────────
# pg = sym.get_point_group()
# print("Point group:", pg.get_label().get_name())
# print()

# # ── Character table (irrational values shown symbolically) ─────────────────
# print("Character table:")
# pg.print_character_table()
# print()

# # ── Rotor classification ───────────────────────────────────────────────────────
# print("Rotor class:", sym.get_rotor_class())
# print()

# # ── Cartesian axes (columns = x, y, z) ────────────────────────────────────────
# print("Cartesian axes (columns = x, y, z):")
# print(sym.get_cartesian_axes())
# print()

# # ── Atom index legend ─────────────────────────────────────────────────────────
# print("Atom index legend (COM-centred coordinates):")
# s.print_atom_list()
# print()

# # ── Geometric atom queries ─────────────────────────────────────────────────
# print("Geometric annotation per found operation:")
# for op in mgr.get_operations():
#     label = op.get_label()
#     name  = label.get_short_name()
#     from schoenflies.operations.operation_label import OperationLabel
#     elem  = label.get_element()
#     if elem in (OperationLabel.Element.ProperRotation,
#                 OperationLabel.Element.ImproperRotation):
#         on_axis = op.get_atoms_on_axis(s)
#         detail  = f"axis {op.get_axis().round(3).tolist()}"
#         if on_axis:
#             detail += f"  |  {len(on_axis)}/{s.num_atoms} atoms on axis: {on_axis}"
#     elif elem == OperationLabel.Element.Reflection:
#         in_plane = op.get_atoms_in_plane(s)
#         detail   = f"normal {op.get_axis().round(3).tolist()}"
#         detail  += f"  |  {len(in_plane)}/{s.num_atoms} atoms in plane"
#         if op.is_molecular_plane(s):
#             detail += "  [molecular plane]"
#     else:
#         detail = ""
#     print(f"  {name:<8} {detail}")
# print()

# # ── summarize() and print_operations() ─────────────────────────────────────
# print("Operations grouped by type (summarize):")
# for key, ops in mgr.summarize().items():
#     print(f"  {key}: {[o.get_label().get_short_name() for o in ops]}")
# print()

# print("Full operations table (print_operations):")
# mgr.print_operations()

# ── Character table generator ──────────────────────────────────────────────
# print_character_table_for(name) accepts any Schoenflies symbol:
#   - Fixed groups:   "C1", "Ci", "Cs", "T", "Td", "Oh", "Ih", "C∞v", "D∞h"
#   - Axial groups:   "Cn", "Cnh", "Cnv", "Sn", "Dn", "Dnh", "Dnd"
#     where n is any integer (groups with n > 10 are generated on-the-fly).
from schoenflies.point_groups.character_table_generator import (
    print_character_table_for,
    parse_point_group_name,
    get_or_generate_point_group,
)

print("\n" + "=" * 60)
print("Character table generator examples")
print("=" * 60)

# 1. A group already in the hardcoded list
print("\n-- C3v (hardcoded) --")
print_character_table_for("C3v")

# 2. A higher-order group generated on-the-fly
print("\n-- C11 (generated, n=11 odd cyclic) --")
print_character_table_for("C11")

# 3. A dihedral group beyond the hardcoded limit
print("\n-- D11h (generated) --")
print_character_table_for("D5h")

# 4. Antiprismatic group
print("\n-- D4d (hardcoded) --")
print_character_table_for("D4d")

# 5. Parse a name without printing, then inspect programmatically
label = parse_point_group_name("D6h")
pg_d6h = get_or_generate_point_group(label)
print(f"\n-- D6h: order={pg_d6h.get_order()}, "
      f"{len(pg_d6h.get_irreps())} irreps --")
print_character_table_for("D6h")