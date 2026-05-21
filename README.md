# schoenflies_python

A Python package for automatic Schoenflies point group determination from molecular coordinates. Given a molecular geometry in `.xyz` format, it identifies the molecule's Schoenflies point group symbol by numerically detecting all present symmetry elements.

Python translation of the C++ library by Luuk Kempen (https://gitlab.com/lkkmpn/schoenflies).

---

## What is a point group?

A **point group** is the complete set of symmetry operations that leave a molecule's geometry unchanged — rotations, reflections, inversions, and combinations thereof. Every molecule belongs to exactly one point group, and its label (e.g. C₂ᵥ, D₆ₕ, Td, Oₕ) encodes its full symmetry in compact notation.

Point group symmetry determines which molecular orbitals can mix, which vibrational modes are IR- or Raman-active, and how a molecule interacts with polarised light. Knowing the point group is a prerequisite for interpreting spectra, predicting reactivity, and building quantum-chemical models.

---

## Installation

```bash
git clone https://github.com/Code-Tomas-Dadikozyan/schoenflies_python.git
cd schoenflies_python
pip install -e .
```

**Requirements:** Python 3.10+, `numpy`, `scipy`

---

## Quick start

```python
from schoenflies import Structure, Symmetry

s = Structure("molecule.xyz")
sym = Symmetry(s)

print(sym.get_point_group().get_label().get_name())   # e.g. "C3v"
```

---

## Usage

### As a Python library

#### Point group determination

```python
from schoenflies import Structure, Symmetry

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
print(pg.get_irreps())        # list of IrrepLabel objects
print(pg.get_characters())    # list[list[float]] — [irrep][operation class]
print(pg.get_unique_operations())  # conjugacy classes (excluding E)
```

#### Character table for any group — no XYZ needed

```python
from schoenflies.point_groups.character_table_generator import (
    parse_point_group_name,
    get_or_generate_point_group,
    print_character_table_for,
)

# Quickest: print directly by name
print_character_table_for("D4h")

# Or get the PointGroup object for any axial group (including high-n)
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

# All found operations
for op in manager.get_operations():
    print(op.get_label().get_short_name())   # "C3", "C3^2", "σv", "i", …
    print(op.get_axis())                     # unit-vector axis / plane normal
    print(op.get_error())                    # worst-case atom mis-mapping distance (Å)

# Filter by type
manager.get_proper_rotations()      # Cn only
manager.get_improper_rotations()    # Sn only
manager.get_reflections()           # σ only
manager.get_inversions()            # i only

# Atoms lying on a symmetry element
structure = sym.get_structure()
for op in manager.get_operations():
    label = op.get_label()
    if label.get_element() == label.Element.Reflection:
        atom_indices = op.get_atoms_in_plane(structure)
    else:
        atom_indices = op.get_atoms_on_axis(structure)
```

#### Basis functions (irreducible representations)

```python
from schoenflies.point_groups.basis_functions import compute_basis_functions

basis = compute_basis_functions(pg)
# Returns dict[irrep_name, {"linear": [...], "quadratic": [...]}]
# e.g. {"A1": {"linear": ["z"], "quadratic": ["z²", "x²+y²"]}, "E": {...}, ...}
for irrep, funcs in basis.items():
    print(irrep, funcs["linear"], funcs["quadratic"])
```

#### Element data

```python
from schoenflies.periodic_table import get_element, get_atomic_number

el = get_element(6)          # Element for carbon
print(el.symbol)             # "C"
print(el.name)               # "carbon"
print(el.mass)               # 12.011
print(el.radius)             # covalent radius in Å
print(el.colour)             # CPK RGB tuple (0–1)

n = get_atomic_number("Fe")  # 26
```

### As a command-line tool

```bash
# Single molecule
schoenflies molecule.xyz

# Multiple files at once
schoenflies tests/files/*.xyz

# Verbose: show rotor class and all found operations
schoenflies -v ammonia.xyz

# Print the character table for the determined point group
schoenflies -ct ammonia.xyz

# Character table with ε-notation (cyclic / Sn groups)
schoenflies -ct --complex ammonia.xyz

# Show principal moments of inertia and Cartesian axes
schoenflies -m ammonia.xyz

# Show which atoms lie on each symmetry axis / mirror plane
schoenflies -od ammonia.xyz

# All flags combined
schoenflies -v -ct -m -od ammonia.xyz

# Force plain-text output (no rich formatting)
schoenflies -ct --plain ammonia.xyz

# Print a character table for any named group — no XYZ file needed
schoenflies -g C3v
schoenflies -g D6h --plain
schoenflies -g Oh --complex
```

#### Full flag reference

| Flag | Description |
|------|-------------|
| `-v`, `--verbose` | Show rotor class and all found symmetry operations |
| `-ct`, `--character-table` | Print the full character table (with basis functions) for the determined point group |
| `--complex` | Use ε-notation in the character table (meaningful for cyclic / Sn groups) |
| `-m`, `--moments` | Show the three principal moments of inertia (Ia, Ib, Ic in u·Å²) and the 3×3 Cartesian axes matrix |
| `-od`, `--operations-detail` | For each symmetry operation list the atom symbols and indices lying on its axis or in its plane |
| `--plain` | Force plain-text output (suppress `rich` table formatting) |
| `-g NAME`, `--group NAME` | Standalone mode: print the character table for a named group without an XYZ file. Accepts all Schoenflies symbols, e.g. `C1`, `Cs`, `C3v`, `D4h`, `S8`, `Oh`, `Ih`, `Cinfv`, `Dinfh`. Mutually exclusive with FILE arguments. |

**Example output** (`schoenflies -v -ct --plain ammonia.xyz`):
```
ammonia.xyz
  Point group : C3v
  Rotor class : ProlateSymmetricTop
  Operations  : 4 found
    C3
    C3^2
    σv
    σv
    σv

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

- Line 1: number of atoms
- Line 2: comment (ignored)
- Lines 3+: element symbol followed by x y z coordinates

The molecule does not need to be pre-centred; the code translates it to its centre of mass automatically.

---

## How the algorithm works

1. **Inertia tensor → principal axes.** The 3×3 inertia tensor is built and diagonalised via `numpy.linalg.eigh`, yielding three principal moments and axes.

2. **Rotor classification.** The degeneracy of the moments classifies the molecule into one of five types: *Linear*, *Spherical Top*, *Prolate Symmetric Top*, *Oblate Symmetric Top*, or *Asymmetric Top*. This prunes the candidate search space before symmetry testing.

3. **Symmetry element detection.** Candidate axes are generated from principal axes, atom positions, and pair midpoints. For high-symmetry spherical tops (Td, Oh, Ih) additional face-centroid axes are added. Each candidate is tested by applying the transformation matrix to every atom and checking that the result maps onto a same-element atom within a tolerance of 10% of the distance to the symmetry element. Elements detected: inversion centre (i), proper rotations Cₙ (n = 2–8 and ∞), mirror planes (σ), and improper rotations Sₙ.

4. **Point group matching.** Detected operation counts are compared against a library of 54+ predefined point groups. The group with the smallest non-negative surplus of operations is selected.

5. **Axis assignment and labelling.** The Cartesian frame is standardised: z along the highest-order proper rotation axis; x chosen to maximise atoms in the xz-plane. Mirror planes and C₂ axes are then labelled (σₕ, σᵥ, σd, C₂′, C₂′′).

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

## Running tests

```bash
python -m pytest tests/ -v
```

The test suite covers 32 reference molecules spanning all major point group families, plus unit tests for matrix construction, operation equality, and character table integrity.

---

## Known limitations

- **Maximum Cₙ order is 8.** Higher-order axes (C₉, C₁₀, …) are not searched. Covers all common chemical cases.
- **Character tables for polyhedral groups are hardcoded.** T, Td, Th, O, Oh, I, Ih, and the linear groups (C∞v, D∞h) use pre-computed tables. All axial groups (Cn, Cnh, Cnv, Sn, Dn, Dnh, Dnd) are generated analytically for any order n.
- **Fixed tolerance.** All geometry checks use a tolerance of 10% of the distance to the symmetry element. Slightly distorted geometries may be misclassified.
- **No visualisation.** This package is the algorithm layer only. The original C++ application includes a full Qt5/OpenGL molecular viewer with real-time symmetry animation; that GUI is not part of this translation.
- **No periodic structures.** Single isolated molecules only; crystal structures and space groups are not supported.

---

## Repository layout

```
schoenflies_python/
├── schoenflies/            ← Python package
│   ├── periodic_table.py   ← Atomic data (118 elements)
│   ├── rotor_class.py      ← RotorClass enum
│   ├── structure.py        ← XYZ loading, centre-of-mass centering
│   ├── symmetry.py         ← Main pipeline (Symmetry class)
│   ├── operations/         ← Operation, OperationLabel, OperationManager
│   └── point_groups/       ← PointGroup, character tables, 54+ definitions
├── tests/
│   ├── files/              ← 32 reference XYZ molecules
│   ├── test_structure.py
│   ├── test_operation.py
│   ├── test_point_groups.py
│   └── test_symmetry.py
├── reference/              ← Original C++ source (read-only)
├── pyproject.toml
└── CHANGELOG.md
```

---

## References

- Original C++ implementation by Luuk Kempen: https://gitlab.com/lkkmpn/schoenflies
- Johansson, M. P. & Veryazov, V. (2017). *Automatic procedure for generating symmetry adapted wavefunctions*. **Journal of Cheminformatics**, 9, 36. https://doi.org/10.1186/s13321-017-0193-3
