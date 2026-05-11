import sys, io
# ensure Unicode output works on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-16"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from schoenflies import Structure, Symmetry

s = Structure("tests\\files\\benzene.xyz")
sym = Symmetry(s)

# Point group label
pg = sym.get_point_group()
print(pg.get_label().get_name())        # "C3v"

# Character table
pg.print_character_table()

# Rotor classification
print(sym.get_rotor_class())            # RotorClass.ProlateSymmetricTop

# Found symmetry operations
for op in sym.get_operation_manager().get_operations():
    print(op.get_label().get_short_name())   # "C3", "sv", ...

# Cartesian axes (columns = x, y, z)
print(sym.get_cartesian_axes())