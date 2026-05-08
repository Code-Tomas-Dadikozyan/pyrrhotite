# schoenflies_python

A Python adaptation of the point group determination library by Luuk Kempen (https://gitlab.com/lkkmpn/schoenflies). Given a molecular geometry in `.xyz` format, it identifies the molecule's Schoenflies point group symbol by numerically detecting all present symmetry elements. The Python implementation follows the structure and logic of the original C++ source as closely as Python allows.

## What are point groups and why do they matter?

A **point group** is the complete set of symmetry operations that leave a molecule's geometry unchanged — rotations, reflections, inversions, and combinations thereof. Every molecule belongs to exactly one point group, and the label for that group (e.g. C₂ᵥ, D₆ₕ, Td, Oₕ) encodes its full symmetry in compact notation.

Point group symmetry is not just an aesthetic classification. It directly determines which molecular orbitals can mix, which vibrational modes are IR- or Raman-active, and how a molecule will interact with polarised light. In practice, knowing a molecule's point group is a prerequisite for interpreting its spectra, predicting its reactivity, and building correct quantum-chemical models.

Determining point groups by hand is straightforward for small molecules but becomes error-prone and tedious for larger or less obvious structures. This project automates the process numerically, reproducing the algorithm described in Johansson & Veryazov (2017).

## Repository layout

```
schoenflies_python/
├── reference/          ← Read-only C++ source (Kempen). Never modified.
├── version1/           ← Archived first Python implementation.
│   └── schoenflies/    ← molecule.py, symmetry_elements.py, point_group.py, utils.py
├── schoenflies/        ← Target package directory for the current implementation.
├── tests/              ← Pytest suite and .xyz test molecules.
├── pyproject.toml
└── CHANGELOG.md
```

The algorithm is implemented across four modules that mirror the separation used in the C++ reference:

| Module | C++ counterpart | Responsibility |
|---|---|---|
| `molecule.py` | `structure.h/cpp` | XYZ parsing, inertia tensor, rotor classification |
| `symmetry_elements.py` | `symmetry/symmetry.h/cpp` + `operations/` | Candidate generation and symmetry element detection |
| `point_group.py` | `symmetry/point_groups/` | Group library, scoring, axis labelling |
| `utils.py` | — | Rotation/reflection matrices, equivalence testing, geometric helpers |

## How the algorithm works

The determination follows five sequential stages that map directly onto the C++ pipeline:

1. **Inertia tensor → principal axes.** The molecule is translated to its centre of mass. Its 3×3 inertia tensor is constructed and diagonalised via `numpy.linalg.eigh`, yielding three principal moments of inertia and the orthogonal axes along which they act.

2. **Rotor classification.** The degeneracy pattern of the three principal moments classifies the molecule into one of five rotor types: *Linear* (one moment is zero), *Spherical Top* (all three equal, e.g. CH₄), *Prolate Symmetric Top* (two equal, longest axis unique, e.g. NH₃), *Oblate Symmetric Top* (two equal, shortest axis unique, e.g. benzene), or *Asymmetric Top* (all different, e.g. H₂O). This classification prunes the candidate search space before any symmetry testing begins.

3. **Symmetry element detection.** Candidate axes are generated from principal axes, atom positions, pair midpoints, and — for high-symmetry spherical tops like C₆₀ — ring centroids and triple centroids. Each candidate is tested by applying the corresponding transformation (Cₙ rotation, reflection, inversion, or Sₙ) to every atom and verifying that the result coincides with another atom of the same element within a tolerance of 0.02 Å. Elements detected: inversion centre (i), proper rotation axes Cₙ (n = 2–8), mirror planes (σ), and improper rotation axes Sₙ. Duplicate and anti-parallel axes are merged after detection.

4. **Point group matching.** The detected element counts are compared against a library of 43 predefined point groups, each stored as a `PGRecord` with required element counts. A scoring function assigns 0 to a perfect match, a positive penalty for surplus elements, and −1 (disqualified) to any group whose required elements are absent. Linear molecules are handled separately as C∞ᵥ or D∞ₕ before the library search. The group with the lowest non-negative score is selected.

5. **Axis assignment and labelling.** The Cartesian frame is standardised: z is placed along the highest-order proper rotation axis; x is chosen to pass through the greatest number of atoms in the xz plane. Mirror planes and C₂ axes are then labelled by their geometric relationships to the principal axis (σₕ, σᵥ, σd, C₂′, C₂′′).

## Installation

**From source:**
```bash
git clone https://github.com/Code-Tomas-Dadikozyan/schoenflies_python.git
cd schoenflies_python
pip install -e .
```

**Dependencies** (installed automatically): `numpy`, `scipy`

## Usage

```python
from schoenflies import Molecule, SymmetryFinder, PointGroupClassifier

mol = Molecule("molecule.xyz")
finder = SymmetryFinder(mol)
elements = finder.find_all()
classifier = PointGroupClassifier(elements)
print(classifier.point_group)   # e.g. "D6h"
```

## Input format

Standard `.xyz` files:

```
3
Water molecule
O   0.000000   0.000000   0.119748
H   0.000000   0.756950  -0.478993
H   0.000000  -0.756950  -0.478993
```

- Line 1: atom count
- Line 2: comment (ignored)
- Lines 3+: element symbol followed by x y z coordinates in Ångströms

The molecule does not need to be pre-centred; the code translates it to its centre of mass automatically.

## Supported point groups

| Family | Groups |
|---|---|
| Non-axial | C₁, Cᵢ, Cₛ |
| Cyclic | C₂, C₃, C₄, C₅, C₆, C₇, C₈ |
| Cyclic with σₕ | C₂ₕ, C₃ₕ, C₄ₕ, C₅ₕ, C₆ₕ |
| Cyclic with σᵥ | C₂ᵥ, C₃ᵥ, C₄ᵥ, C₅ᵥ, C₆ᵥ |
| Improper axes | S₄, S₆, S₈ |
| Dihedral | D₂, D₃, D₄, D₅, D₆ |
| Dihedral with σₕ | D₂ₕ, D₃ₕ, D₄ₕ, D₅ₕ, D₆ₕ |
| Dihedral with σd | D₂d, D₃d, D₄d, D₅d, D₆d |
| Cubic | Td, T, Tₕ, O, Oₕ |
| Icosahedral | I, Iₕ |
| Linear | C∞ᵥ, D∞ₕ |

## Known limitations

- **Tolerance sensitivity.** All geometry checks use a fixed tolerance of 0.02 Å. Molecules with near-symmetry (e.g. slightly distorted geometries from a relaxed scan) may be misclassified. This value is defined in `utils.py`.
- **Maximum Cₙ order = 8.** Axes of order higher than 8 are not searched. This covers all chemically common cases but excludes exotic or hypothetical molecules with very high-order axes.
- **No periodic structures.** The algorithm operates on a single isolated molecule. Crystal structures, unit cells, and space groups are not supported.
- **Geometry must be a minimum or stationary point.** Arbitrary snapshots from a molecular dynamics trajectory may carry numerical noise that triggers false symmetry failures.

## References

- Johansson, M. P. & Veryazov, V. (2017). *Automatic procedure for generating symmetry adapted wavefunctions*. **Journal of Cheminformatics**, 9, 36. https://doi.org/10.1186/s13321-017-0193-3
- Original C++ implementation by Luuk Kempen: https://gitlab.com/lkkmpn/schoenflies
