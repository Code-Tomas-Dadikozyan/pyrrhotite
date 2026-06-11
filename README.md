# pyrrhotite

Automatic Schoenflies point group determination, character table generation, and
3-D molecule visualization — from a plain `.xyz` file or from nothing at all.

Given a molecular geometry in `.xyz` format, `pyrrhotite` identifies the molecule's
Schoenflies point group symbol by numerically detecting all present symmetry
elements (rotations, reflections, inversions, and improper rotations), then builds
the full character table for that group — even for groups it has never seen before.

---

## Where this project came from

`pyrrhotite` started as a Python translation of the C++ library `schoenflies` by
Luuk Kempen (https://gitlab.com/lkkmpn/schoenflies), which detects symmetry
operations from an `.xyz` file and visualizes them on the molecule.

The two projects have since diverged:

| | Luuk Kempen's `schoenflies` (C++) | `pyrrhotite` (this project) |
|---|---|---|
| Point group determination from `.xyz` | ✅ | ✅ |
| Character table generation | ❌ | ✅ — for **any** of the 18 Schoenflies classes, including arbitrary order Cₙ groups, with or without an `.xyz` file |
| HTML / LaTeX export of character tables | ❌ | ✅ |
| 3-D visualizer | ✅ — shows the molecule **and overlays the detected symmetry operations** (axes, planes) | ✅ — shows the molecule with an orientation gizmo and optional element labels (symmetry-operation overlays are not yet implemented) |
| Sample molecule library | ❌ | ✅ — 32 bundled `.xyz` files with one-line helpers |

In short: if you need to *see* the symmetry operations drawn on a molecule, the
original C++ tool is currently the better choice. If you need character tables —
generated on demand for any point group, with or without a structure — `pyrrhotite`
is the tool for that.

---

## Installation

```bash
pip install pyrrhotite
```

**Requirements:** Python 3.10+

`pip install pyrrhotite` automatically installs the core dependencies:

| Package | Used for |
|---|---|
| `numpy` | linear algebra (inertia tensor, symmetry-operation matrices) |
| `scipy` | numerical helpers used during symmetry detection |
| `rich` | coloured/formatted terminal output for character tables (optional at runtime — plain-text output is used as a fallback if `rich` isn't available) |

The 3-D visualizer needs extra graphics libraries that aren't installed by default.
To enable it:

```bash
pip install 'pyrrhotite[vis]'
```

| Extra package | Used for |
|---|---|
| `PyQt6` | application window and event loop |
| `PyOpenGL` | OpenGL bindings for rendering atoms, bonds, and the axis gizmo |
| `pyrr` | matrix/vector math for the camera and arcball rotation |
| `matplotlib` | colour utilities for atom/bond rendering |

For development (running the test suite):

```bash
pip install 'pyrrhotite[dev]'   # installs pytest
```

---

## Quick start

```python
from pyrrhotite import Structure, Symmetry

s = Structure("molecule.xyz")
sym = Symmetry(s)

print(sym.point_group.label.name)   # e.g. "C3v"
```

Or from the command line:

```bash
pyrrhotite molecule.xyz
pyrrhotite -v -ct ammonia.xyz   # verbose + character table
```

---

## What is a point group?

A **point group** is the complete set of symmetry operations that leave a
molecule's geometry unchanged. Every molecule belongs to exactly one point group,
and its label (e.g. C₂ᵥ, D₆ₕ, Td, Oₕ) encodes its full symmetry in compact notation.

Point group symmetry determines which molecular orbitals can mix, which vibrational
modes are IR- or Raman-active, and how a molecule interacts with polarised light.
The **character table** of a point group is the lookup table that encodes all of
this — see [Character table](#character-table) below.

---

## Usage

### Python library

#### Point group determination

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

#### Character table

A character table is a small grid that summarises everything the point group tells
you about the molecule: which combinations of atomic orbitals are allowed to mix,
and which vibrations/rotations show up in infrared or Raman spectra.

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

#### Character table for any group — no XYZ needed

You can also generate a character table for a named point group without loading
any molecule. This works for all 18 Schoenflies classes — the seven axial families
(Cn, Cnh, Cnv, Sn, Dn, Dnh, Dnd) are generated analytically for any order, and the
rest (cubic, icosahedral, linear, and the low-symmetry groups) come from a built-in
table.

```python
from pyrrhotite.character_tables import (
    get_or_generate_point_group,
    print_character_table_for,
)

print_character_table_for("D4h")

pg = get_or_generate_point_group("C12v")
pg.print_character_table()
```

Or from the command line:

```bash
pyrrhotite -g C3v
pyrrhotite -g D6h --plain
pyrrhotite -g C12v   # arbitrary order — generated on the fly
```

##### Exporting character tables (HTML / LaTeX)

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

#### Generating idealized structures

For testing or demonstration, `pyrrhotite` can build an idealized `Structure`
that has, by construction, a requested axial point group symmetry — a ring (or
combination of rings) of placeholder atoms arranged as a Cn, Cnh, Cnv, Sn, Dn,
Dnh, or Dnd structure for any supported order n. The geometry of each family is
modelled on a real molecule with that symmetry (e.g. ammonia-like apex+ring
substituents for Cnv, benzene's ring+substituent for Cnh, ferrocene's metal-hub
sandwich for Dn/Dnh/Dnd/Sn), so the generated structure also has a plausible
bonding pattern in the 3-D viewer — including element choices that roughly
match each atom's bonding degree (H for degree 1, O for degree 2, N for degree
3, C for degree 4, S for degree 5-6, and a metal-like hub for higher degrees)
— rather than an over-connected uniform ring:

```python
from pyrrhotite import generate_idealized_structure, write_xyz, Symmetry
from pyrrhotite.structure_generator import format_xyz

s = generate_idealized_structure("D12h")    # build an idealized D12h structure
print(Symmetry(s).point_group.label.name)   # "D12h"

print(format_xyz(s))                        # get it as XYZ text, no file needed
write_xyz(s, "d12h.xyz")                    # or write it straight to an .xyz file
```

To preview a generated structure without writing it to disk first, use
`visualize_idealized_structure` (requires `pip install 'pyrrhotite[vis]'`):

```python
from pyrrhotite import visualize_idealized_structure

visualize_idealized_structure("D9d")                  # opens the 3-D viewer
visualize_idealized_structure("D9d", show_labels=True)
```

Or from the command line, combined with `-g`:

```bash
pyrrhotite -g C12v --xyz                  # print the generated structure as XYZ to stdout
pyrrhotite -g D9d --xyz d9d.xyz           # save the generated structure as XYZ to a file
pyrrhotite d9d.xyz -v                     # then analyse the generated file as usual
pyrrhotite -g D9d --visualize             # preview the generated structure directly
```

See section 14 of `example_usage.py` for a runnable demo covering
`format_xyz`, `write_xyz`, round-trip detection across all seven axial
families, custom radius/height/element, and the error cases for
unsupported groups/orders.

#### Rotor classification and principal axes

Before searching for symmetry operations, `pyrrhotite` classifies the molecule's
overall shape from its moments of inertia — this narrows down which symmetry
elements are even possible.

```python
print(sym.rotor_class)            # RotorClass.ProlateSymmetricTop

pm = sym.principal_moments        # np.ndarray shape (3,) — Ia ≤ Ib ≤ Ic in u·Å²
axes = sym.principal_axes         # np.ndarray shape (3, 3) — eigenvectors as columns
cart = sym.cartesian_axes         # 3×3 matrix [x | y | z] in the conventional frame
```

#### Symmetry operations

Every symmetry operation found on the molecule (rotation axes, mirror planes,
inversion centre, improper rotation axes) is available individually, with its axis
and a numerical error estimate showing how well the molecule actually matches that
symmetry.

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

#### Basis functions

Basis functions tell you, for each irreducible representation (irrep), which `x`,
`y`, `z` coordinates, rotations, or quadratic combinations (`x²`, `xy`, …) transform
the same way — useful for working out IR/Raman selection rules and orbital
symmetries.

```python
from pyrrhotite.point_groups.basis_functions import compute_basis_functions

basis = compute_basis_functions(pg)
# Returns dict[irrep_name, {"linear": [...], "quadratic": [...]}]
for irrep, funcs in basis.items():
    print(irrep, funcs["linear"], funcs["quadratic"])
```

#### Element data

```python
from pyrrhotite.periodic_table import get_element, get_atomic_number

el = get_element(6)
print(el.symbol)   # "C"
print(el.mass)     # 12.011

n = get_atomic_number("Fe")   # 26
```

#### 3-D visualizer

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

If they aren't installed, `visualize()` raises an `ImportError` with instructions
instead of crashing.

> **Note:** unlike Luuk Kempen's original visualizer, this viewer does not (yet)
> draw the detected symmetry elements (axes, mirror planes) on top of the molecule
> — it shows only the molecule itself, the axis gizmo, and optional atom labels.

#### Sample molecules

For learning and quick experiments, `pyrrhotite` bundles 32 `.xyz` files covering
all major point-group families (water, ammonia, benzene, ferrocene,
buckminsterfullerene, ...). These are exposed through a few convenience functions:

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

### Command-line tool

```bash
pyrrhotite molecule.xyz
pyrrhotite tests/files/*.xyz

pyrrhotite -v ammonia.xyz             # rotor class + all operations
pyrrhotite -ct ammonia.xyz            # character table
pyrrhotite -ct --complex ammonia.xyz
pyrrhotite -m ammonia.xyz             # principal moments and axes
pyrrhotite -od ammonia.xyz            # atoms on each symmetry element
pyrrhotite -v -ct -m -od ammonia.xyz

pyrrhotite -g C3v                     # character table with no XYZ file
pyrrhotite -g D6h --plain

pyrrhotite ammonia.xyz --visualize    # open the 3-D viewer after analysis
pyrrhotite ammonia.xyz -vis -l        # ... with element labels shown
```

| Flag | Description |
|------|-------------|
| `-v`, `--verbose` | Show rotor class and all found symmetry operations |
| `-ct`, `--character-table` | Print the full character table (with basis functions) |
| `--complex` | Use ε-notation in the character table |
| `-m`, `--moments` | Show principal moments of inertia and Cartesian axes matrix |
| `-od`, `--operations-detail` | List atoms lying on each symmetry axis or mirror plane |
| `--plain` | Force plain-text output (suppress `rich` formatting) |
| `-g NAME`, `--group NAME` | Print character table for a named group without an XYZ file |
| `--visualize`, `-vis` | Open an interactive 3-D viewer after analysis (requires `pip install 'pyrrhotite[vis]'`) |
| `--labels`, `-l` | Show element symbols on atoms in the 3-D viewer (implies `--visualize`) |

**Example output** (`pyrrhotite -v -ct --plain ammonia.xyz`):

```
ammonia.xyz
  Point group : C3v
  Rotor class : ProlateSymmetricTop
  Operations  : 4 found
    C3
    C3^2
    σv  (×3)

C3v |      E |   2 C3 |   3 σv | Lin/Rot |         Quadratic
--------------------------------------------------------------
A1  |      1 |      1 |      1 |       z |         z², x²+y²
A2  |      1 |      1 |     -1 |      Rz |
E   |      2 |     -1 |      0 | x, y, Rx, Ry | x²-y², xy, xz, yz
```

---

## Input format

Standard `.xyz` files (coordinates in Ångströms):

```
3
Water molecule
O   0.000000   0.000000   0.119748
H   0.000000   0.756950  -0.478993
H   0.000000  -0.756950  -0.478993
```

The molecule does not need to be pre-centred; coordinates are translated to the
centre of mass automatically.

---

## Supported point groups

Symmetry **detection** (from an `.xyz` file) currently covers:

| Family | Groups |
|---|---|
| Non-axial | C₁, Cᵢ, Cₛ |
| Cyclic | C₂ – C₂₀* |
| Cyclic with σₕ | C₂ₕ – C₂₀ₕ* |
| Cyclic with σᵥ | C₂ᵥ – C₂₀ᵥ* |
| Improper axes | S₄ – S₂₀* (even orders) |
| Dihedral | D₂ – D₂₀* |
| Dihedral with σₕ | D₂ₕ – D₂₀ₕ*, D∞ₕ |
| Dihedral with σd | D₃d – D₂₀d* |
| Cubic | T, Td, Tₕ, O, Oₕ |
| Icosahedral | I, Iₕ |
| Linear | C∞ᵥ, D∞ₕ |

\* The maximum detectable rotation order is **adaptive**: for each candidate
axis, `pyrrhotite` looks for the largest "ring" of symmetry-equivalent atoms
(same element, same distance from the axis, same position along the axis)
and only tests Cₙ orders up to that ring size, capped at n = 20. So detecting
a Cₙ axis still requires an actual n-fold ring of equivalent atoms in the
structure — `pyrrhotite -g C20v` works for *any* molecule shape via the
on-the-fly character table generator below, but *detecting* C20v from
coordinates requires a molecule with a genuine 20-fold ring.

**Character table generation** is more general: all 18 Schoenflies classes are
supported, and the seven axial families (Cn, Cnh, Cnv, Sn, Dn, Dnh, Dnd) are
generated analytically for *any* order n ≥ 2 — not just the ranges above. So
`pyrrhotite -g C30v` works even for orders beyond the detection cap.

---

## How the algorithm works

1. **Inertia tensor → principal axes.** The 3×3 inertia tensor is diagonalised via
   `numpy.linalg.eigh`, yielding three principal moments and axes.
2. **Rotor classification.** Degeneracy of the moments classifies the molecule into
   one of five types (*Linear*, *Spherical Top*, *Prolate Symmetric Top*, *Oblate
   Symmetric Top*, *Asymmetric Top*), pruning the candidate search space.
3. **Symmetry element detection.** Candidate axes are generated from principal
   axes, atom positions, and pair midpoints. For each candidate axis, the
   rotation orders tested are bounded by the size of the largest ring of
   symmetry-equivalent atoms found around it (capped at n = 20). Each candidate
   is tested by applying the transformation matrix and checking that every atom
   maps onto a same-element atom within a tolerance of 10% of the distance to
   the symmetry element (tightened for high-order axes to avoid confusing
   neighbouring orders, e.g. C9 vs C8).
4. **Point group matching.** Detected operation counts are compared against a
   library of point groups. If the operations don't match any hardcoded group
   (e.g. an axis order greater than the hardcoded range), a character table is
   generated on the fly for the inferred family and order. The group with the
   smallest non-negative surplus of operations is selected.
5. **Axis assignment and labelling.** The Cartesian frame is standardised (z along
   the highest-order proper rotation; x to maximise atoms in the xz-plane) and
   operations are labelled (σₕ, σᵥ, σd, C₂′, C₂″).

---

## Known limitations

- Symmetry **detection** from `.xyz` coordinates adapts the maximum tested
  rotation order to the molecule's geometry (capped at n = 20, see
  [Supported point groups](#supported-point-groups)) — a Cₙ axis can only be
  detected if the molecule actually has an n-fold ring of equivalent atoms.
  **Character table generation** for named groups has no such limit for the
  axial families.
  - The n = 20 cap isn't an arbitrary round number that could just be raised:
    the per-degree validation tolerance shrinks roughly as 1/n², and beyond
    n ≈ 20 it approaches the noise floor of typical `.xyz` coordinates
    (3-4 decimal places, propagated through inertia-tensor diagonalization
    and Rodrigues rotation), risking both missed high-order axes and renewed
    confusion between neighbouring orders.
  - Even without that limit, a Cₙ axis can only be *detected* if the molecule
    actually contains an n-fold ring of symmetry-equivalent atoms — raising
    the cap only matters for molecules that physically have such rings.
  - The ring search is O(atoms²) per candidate axis (on top of the existing
    O(atoms²) candidate generation), so a higher cap increases the constant
    factor for large molecules without changing the overall complexity.
- Fixed 10% tolerance — slightly distorted geometries may be misclassified.
- Single isolated molecules only; crystal structures and space groups are not
  supported.
- The 3-D visualizer shows the molecule and an axis gizmo, but does not yet draw
  the detected symmetry elements (rotation axes, mirror planes) on top of it.

---

## Running tests

```bash
python -m pytest tests/ -v
```

---

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE) for details.

---

## References

- Original C++ implementation by Luuk Kempen: https://gitlab.com/lkkmpn/schoenflies
- Johansson, M. P. & Veryazov, V. (2017). *Automatic procedure for generating
  symmetry adapted wavefunctions*. **Journal of Cheminformatics**, 9, 36.
  https://doi.org/10.1186/s13321-017-0193-3
