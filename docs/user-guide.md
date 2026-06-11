# User Guide

This page walks through the Python API in depth. For the command-line tool, see
[Getting Started](getting-started.md#command-line-reference).

## Point group determination

```python
from pyrrhotite import Structure, Symmetry

s = Structure("ammonia.xyz")
sym = Symmetry(s)

pg = sym.point_group
print(pg.label.name)        # "C3v"
print(pg.order)              # 6  (total number of symmetry operations)
```

`Structure` loads the atoms and coordinates from an `.xyz` file and automatically
re-centres the molecule on its centre of mass. `Symmetry` runs the full detection
pipeline and exposes the result as a `PointGroup`.

## Character tables

A character table is a small grid that summarises everything the point group
tells you about the molecule: which combinations of atomic orbitals are allowed
to mix, and which vibrations/rotations show up in infrared or Raman spectra.

```python
# Print with rich formatting (falls back to plain if rich is not installed)
pg.print_character_table()

# Plain text
pg.print_character_table(plain=True)

# ε-notation for cyclic / Sn groups
pg.print_character_table(complex=True)

# Access the data directly
print(pg.irreps)             # list of IrrepLabel objects
print(pg.characters)         # list[list[float]] — [irrep][operation class]
print(pg.unique_operations)  # conjugacy classes (excluding E)
```

### Character tables for any group — no XYZ needed

You can also generate a character table for a named point group without loading
any molecule. This works for all 18 Schoenflies classes — the seven axial
families (Cn, Cnh, Cnv, Sn, Dn, Dnh, Dnd) are generated analytically for any
order, and the rest (cubic, icosahedral, linear, and the low-symmetry groups)
come from a built-in table.

=== "Python"

    ```python
    from pyrrhotite.character_tables import (
        get_or_generate_point_group,
        print_character_table_for,
    )

    print_character_table_for("D4h")

    pg = get_or_generate_point_group("C12v")
    pg.print_character_table()
    ```

=== "Command line"

    ```bash
    pyrrhotite -g C3v
    pyrrhotite -g D6h --plain
    pyrrhotite -g C12v   # arbitrary order — generated on the fly
    ```

### Exporting character tables (HTML / LaTeX)

For reports, slides, or web pages, character tables can be exported directly to
HTML or LaTeX:

```python
from pyrrhotite.character_tables import format_html, save_html, format_latex, save_latex

print(format_html(["C3v", "D6h"]))          # HTML string, ready to embed in a page
save_html(["Oh"], "oh_table.html")          # write a standalone HTML file

print(format_latex(["C3v", "D6h"]))         # LaTeX string (requires \usepackage{booktabs,amsmath})
save_latex(["Oh"], "oh_table.tex")
```

The same formatters are also runnable as standalone scripts:

```bash
python -m pyrrhotite.character_tables.html_formatter C3v D6h
python -m pyrrhotite.character_tables.html_formatter Oh --save
python -m pyrrhotite.character_tables.latex_formatter Oh D4h --save tables.tex
```

---

## Rotor classification and principal axes

Before searching for symmetry operations, `pyrrhotite` classifies the molecule's
overall shape from its moments of inertia — this narrows down which symmetry
elements are even possible.

```python
print(sym.rotor_class)            # RotorClass.ProlateSymmetricTop

pm = sym.principal_moments        # np.ndarray shape (3,) — Ia ≤ Ib ≤ Ic in u·Å²
axes = sym.principal_axes         # np.ndarray shape (3, 3) — eigenvectors as columns
cart = sym.cartesian_axes         # 3×3 matrix [x | y | z] in the conventional frame
```

---

## Symmetry operations

Every symmetry operation found on the molecule (rotation axes, mirror planes,
inversion centre, improper rotation axes) is available individually, with its
axis and a numerical error estimate showing how well the molecule actually
matches that symmetry.

```python
manager = sym.operation_manager

for op in manager.operations:
    print(op.label.short_name)   # "C3", "C3^2", "σv", "i", …
    print(op.axis)                # unit-vector axis / plane normal
    print(op.error)               # worst-case atom mis-mapping distance (Å)

manager.proper_rotations
manager.improper_rotations
manager.reflections
manager.inversions
```

---

## Basis functions

Basis functions tell you, for each irreducible representation (irrep), which
`x`, `y`, `z` coordinates, rotations, or quadratic combinations (`x²`, `xy`, …)
transform the same way — useful for working out IR/Raman selection rules and
orbital symmetries.

```python
from pyrrhotite.point_groups.basis_functions import compute_basis_functions

basis = compute_basis_functions(pg)
# Returns dict[irrep_name, {"linear": [...], "quadratic": [...]}]
for irrep, funcs in basis.items():
    print(irrep, funcs["linear"], funcs["quadratic"])
```

---

## Element data

```python
from pyrrhotite.periodic_table import get_element, get_atomic_number

el = get_element(6)
print(el.symbol)   # "C"
print(el.mass)     # 12.011

n = get_atomic_number("Fe")   # 26
```

---

## 3-D visualizer

`pyrrhotite` includes a small interactive viewer for checking *what the molecule
actually looks like* before or after analysis. It draws atoms as colour-coded
spheres, bonds as cylinders, and a small red/green/blue arrow gizmo in the corner
showing the x/y/z axes.

```python
from pyrrhotite import Structure, visualize

s = Structure("ammonia.xyz")
visualize(s)                      # opens a window
visualize(s, show_labels=True)    # also overlay element symbols (N, H, H, H, ...)
```

Controls: **left-click and drag** to rotate the molecule, **scroll** to zoom.

This requires the optional `vis` dependencies (PyQt6, PyOpenGL, pyrr):

```bash
pip install 'pyrrhotite[vis]'
```

If they aren't installed, `visualize()` raises an `ImportError` with
instructions instead of crashing.

!!! note
    Unlike Luuk Kempen's original visualizer, this viewer does not (yet) draw
    the detected symmetry elements (axes, mirror planes) on top of the molecule
    — it shows only the molecule itself, the axis gizmo, and optional atom
    labels.

---

## Sample molecules

For learning and quick experiments, `pyrrhotite` bundles 32 `.xyz` files
covering all major point-group families (water, ammonia, benzene, ferrocene,
buckminsterfullerene, ...). These are exposed through a few convenience
functions:

```python
from pyrrhotite import (
    list_sample_molecules,
    load_sample,
    analyse_sample,
    visualize_sample,
    show_character_table_sample,
)

list_sample_molecules()        # ['E-hex-3-ene', 'adamantane', 'ammonia', ...]

s = load_sample("benzene")     # returns a Structure
analyse_sample("benzene")      # prints point group + rotor class
show_character_table_sample("benzene")   # prints the character table

visualize_sample("buckminsterfullerene")  # opens the 3-D viewer (requires [vis])
analyse_sample()               # no name -> picks a random sample molecule
```
