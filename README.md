# pyrrhotite

Automatic Schoenflies point group determination from molecular coordinates.

Given a molecular geometry in `.xyz` format, `pyrrhotite` identifies the molecule's Schoenflies point group symbol by numerically detecting all present symmetry elements (rotations, reflections, inversions, and improper rotations).

Python adaptation of the C++ library by Luuk Kempen (https://gitlab.com/lkkmpn/schoenflies).

---

## Installation

```bash
pip install pyrrhotite
```

**Requirements:** Python 3.10+

---

## Quick start

```python
from pyrrhotite import Structure, Symmetry

s = Structure("molecule.xyz")
sym = Symmetry(s)

print(sym.get_point_group().get_label().get_name())   # e.g. "C3v"
```

Or from the command line:

```bash
pyrrhotite molecule.xyz
pyrrhotite -v -ct ammonia.xyz   # verbose + character table
```

---

## What is a point group?

A **point group** is the complete set of symmetry operations that leave a molecule's geometry unchanged. Every molecule belongs to exactly one point group, and its label (e.g. C₂ᵥ, D₆ₕ, Td, Oₕ) encodes its full symmetry in compact notation.

Point group symmetry determines which molecular orbitals can mix, which vibrational modes are IR- or Raman-active, and how a molecule interacts with polarised light.

---

## Usage

### Python library

#### Point group determination

```python
from pyrrhotite import Structure, Symmetry

s = Structure("ammonia.xyz")
sym = Symmetry(s)

pg = sym.get_point_group()
print(pg.get_label().get_name())        # "C3v"
print(pg.get_order())                   # 6  (total number of symmetry operations)
```

#### Character table

```python
# Print with rich formatting (falls back to plain if rich is not installed)
pg.print_character_table()

# Plain text
pg.print_character_table(plain=True)

# ε-notation for cyclic / Sn groups
pg.print_character_table(complex=True)

# Access the data directly
print(pg.get_irreps())             # list of IrrepLabel objects
print(pg.get_characters())         # list[list[float]] — [irrep][operation class]
print(pg.get_unique_operations())  # conjugacy classes (excluding E)
```

#### Character table for any group — no XYZ needed

```python
from pyrrhotite.point_groups.character_table_generator import (
    parse_point_group_name,
    get_or_generate_point_group,
    print_character_table_for,
)

print_character_table_for("D4h")

label = parse_point_group_name("C12v")
pg = get_or_generate_point_group(label)
pg.print_character_table()
```

Accepts all 18 Schoenflies classes: `C1`, `Cs`, `Ci`, `Cn`, `Cnh`, `Cnv`, `Sn`, `Dn`, `Dnh`, `Dnd`, `T`, `Td`, `Th`, `O`, `Oh`, `I`, `Ih`, `Cinfv` / `C∞v`, `Dinfh` / `D∞h`.

#### Rotor classification and principal axes

```python
print(sym.get_rotor_class())            # RotorClass.ProlateSymmetricTop

pm = sym.get_principal_moments()        # np.ndarray shape (3,) — Ia ≤ Ib ≤ Ic in u·Å²
axes = sym.get_principal_axes()         # np.ndarray shape (3, 3) — eigenvectors as columns
cart = sym.get_cartesian_axes()         # 3×3 matrix [x | y | z] in the conventional frame
```

#### Symmetry operations

```python
manager = sym.get_operation_manager()

for op in manager.get_operations():
    print(op.get_label().get_short_name())   # "C3", "C3^2", "σv", "i", …
    print(op.get_axis())                     # unit-vector axis / plane normal
    print(op.get_error())                    # worst-case atom mis-mapping distance (Å)

manager.get_proper_rotations()
manager.get_improper_rotations()
manager.get_reflections()
manager.get_inversions()
```

#### Basis functions

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

### Command-line tool

```bash
pyrrhotite molecule.xyz
pyrrhotite tests/files/*.xyz

pyrrhotite -v ammonia.xyz          # rotor class + all operations
pyrrhotite -ct ammonia.xyz         # character table
pyrrhotite -ct --complex ammonia.xyz
pyrrhotite -m ammonia.xyz          # principal moments and axes
pyrrhotite -od ammonia.xyz         # atoms on each symmetry element
pyrrhotite -v -ct -m -od ammonia.xyz

pyrrhotite -g C3v                  # character table with no XYZ file
pyrrhotite -g D6h --plain
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

The molecule does not need to be pre-centred; coordinates are translated to the centre of mass automatically.

---

## Supported point groups

| Family | Groups |
|---|---|
| Non-axial | C₁, Cᵢ, Cₛ |
| Cyclic | C₂ – C₁₀ |
| Cyclic with σₕ | C₂ₕ – C₁₀ₕ |
| Cyclic with σᵥ | C₂ᵥ – C₆ᵥ |
| Improper axes | S₄, S₆, S₈ |
| Dihedral | D₂ – D₆ |
| Dihedral with σₕ | D₂ₕ – D₁₀ₕ, D∞ₕ |
| Dihedral with σd | D₃d – D₁₀d |
| Cubic | T, Td, Tₕ, O, Oₕ |
| Icosahedral | I, Iₕ |
| Linear | C∞ᵥ, D∞ₕ |

---

## How the algorithm works

1. **Inertia tensor → principal axes.** The 3×3 inertia tensor is diagonalised via `numpy.linalg.eigh`, yielding three principal moments and axes.
2. **Rotor classification.** Degeneracy of the moments classifies the molecule into one of five types (*Linear*, *Spherical Top*, *Prolate Symmetric Top*, *Oblate Symmetric Top*, *Asymmetric Top*), pruning the candidate search space.
3. **Symmetry element detection.** Candidate axes are generated from principal axes, atom positions, and pair midpoints. Each candidate is tested by applying the transformation matrix and checking that every atom maps onto a same-element atom within a tolerance of 10% of the distance to the symmetry element.
4. **Point group matching.** Detected operation counts are compared against a library of 54+ predefined point groups. The group with the smallest non-negative surplus of operations is selected.
5. **Axis assignment and labelling.** The Cartesian frame is standardised (z along the highest-order proper rotation; x to maximise atoms in the xz-plane) and operations are labelled (σₕ, σᵥ, σd, C₂′, C₂′′).

---

## Known limitations

- Maximum Cₙ order searched is 8.
- Character tables for polyhedral groups (T, Td, Th, O, Oh, I, Ih) and linear groups are hardcoded; all axial groups are generated analytically.
- Fixed 10% tolerance — slightly distorted geometries may be misclassified.
- Single isolated molecules only; crystal structures and space groups are not supported.

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
- Johansson, M. P. & Veryazov, V. (2017). *Automatic procedure for generating symmetry adapted wavefunctions*. **Journal of Cheminformatics**, 9, 36. https://doi.org/10.1186/s13321-017-0193-3
