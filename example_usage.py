import sys, io
# ensure Unicode output works on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-16"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from schoenflies import Structure, Symmetry

s = Structure("tests\\files\\benzene.xyz")
sym = Symmetry(s)
mgr = sym.get_operation_manager()

# ── Point group ────────────────────────────────────────────────────────────────
pg = sym.get_point_group()
print("Point group:", pg.get_label().get_name())
print()

# ── Character table (irrational values shown symbolically) ─────────────────
print("Character table:")
pg.print_character_table()
print()

# ── Rotor classification ───────────────────────────────────────────────────────
print("Rotor class:", sym.get_rotor_class())
print()

# ── Cartesian axes (columns = x, y, z) ────────────────────────────────────────
print("Cartesian axes (columns = x, y, z):")
print(sym.get_cartesian_axes())
print()

# ── Atom index legend ─────────────────────────────────────────────────────────
print("Atom index legend (COM-centred coordinates):")
s.print_atom_list()
print()

# ── Geometric atom queries ─────────────────────────────────────────────────
print("Geometric annotation per found operation:")
for op in mgr.get_operations():
    label = op.get_label()
    name  = label.get_short_name()
    from schoenflies.operations.operation_label import OperationLabel
    elem  = label.get_element()
    if elem in (OperationLabel.Element.ProperRotation,
                OperationLabel.Element.ImproperRotation):
        on_axis = op.get_atoms_on_axis(s)
        detail  = f"axis {op.get_axis().round(3).tolist()}"
        if on_axis:
            detail += f"  |  {len(on_axis)}/{s.num_atoms} atoms on axis: {on_axis}"
    elif elem == OperationLabel.Element.Reflection:
        in_plane = op.get_atoms_in_plane(s)
        detail   = f"normal {op.get_axis().round(3).tolist()}"
        detail  += f"  |  {len(in_plane)}/{s.num_atoms} atoms in plane"
        if op.is_molecular_plane(s):
            detail += "  [molecular plane]"
    else:
        detail = ""
    print(f"  {name:<8} {detail}")
print()

# ── summarize() and print_operations() ─────────────────────────────────────
print("Operations grouped by type (summarize):")
for key, ops in mgr.summarize().items():
    print(f"  {key}: {[o.get_label().get_short_name() for o in ops]}")
print()

print("Full operations table (print_operations):")
mgr.print_operations()