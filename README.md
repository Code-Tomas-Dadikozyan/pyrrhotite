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

```python
from schoenflies import Structure, Symmetry

s = Structure("ammonia.xyz")
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
```

**Character table output** (ammonia, C3v):
```
C3v |   2 C3 |   3 sv
---------------------
A1  |      1 |      1
A2  |      1 |      1
E   |      2 |     -1
```

### As a command-line tool

```bash
# Single molecule
schoenflies molecule.xyz

# Multiple files
schoenflies tests/files/*.xyz

# Verbose: show rotor class and all found operations
schoenflies -v ammonia.xyz
```

**Example output:**
```
ammonia.xyz: C3v

# with -v:
ammonia.xyz
  Point group : C3v
  Rotor class : ProlateSymmetricTop
  Operations  : 4 found
    C3
    sv
    sv
    sv
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
- **Character tables are hardcoded.** Only the 54+ listed groups have character tables. Arbitrary or exotic groups are not supported.
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
