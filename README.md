# schoenflies_python
This script handles automatic point group determination for a molecular structure described in a `.xyz` file. It is a Python adaptation of the repository made by Luuk Kempen (https://gitlab.com/lkkmpn/schoenflies).

## What are point groups and why do they matter?

A **point group** is the complete set of symmetry operations that leave a molecule's geometry unchanged — rotations, reflections, inversions, and combinations thereof. Every molecule belongs to exactly one point group, and the label for that group (e.g. C₂ᵥ, D₆ₕ, Tₐ, Oₕ) encodes its full symmetry in compact notation.

Point group symmetry is not just an aesthetic classification. It directly determines which molecular orbitals can mix, which vibrational modes are IR- or Raman-active, and how a molecule will interact with polarised light. In practice, knowing a molecule's point group is a prerequisite for interpreting its spectra, predicting its reactivity, and building correct quantum-chemical models.

Determining point groups by hand is straightforward for small molecules but becomes error-prone and tedious for larger or less obvious structures. This project automates the process numerically, reproducing the algorithm described in Johansson & Veryazov (2017) in pure Python.

## How the algorithm works

The determination follows five sequential stages:

1. **Inertia tensor → principal axes.** The molecule is translated to its centre of mass. Its 3×3 inertia tensor is constructed and diagonalised (via `numpy.linalg.eigh`), yielding three principal moments of inertia and the orthogonal axes along which they act. These axes are the natural coordinate frame for the molecule.

2. **Rotor classification.** The degeneracy pattern of the three principal moments classifies the molecule into one of four rotor types: *Linear* (one moment is zero), *Spherical Top* (all three equal, e.g. CH₄), *Symmetric Top* (two equal, one different — prolate like NH₃ or oblate like benzene), or *Asymmetric Top* (all different, e.g. H₂O). This classification dramatically prunes the search space for symmetry elements.

3. **Symmetry element detection.** Candidate axes and planes are tested numerically. For each candidate, every atom is transformed (rotated or reflected) and the result is checked for coincidence with another atom of the same element within a tolerance of 0.02 Å. Elements searched include proper rotation axes Cₙ (n = 2–8), mirror planes (σ), an inversion centre (i), and improper rotation axes Sₙ. The rotor class determines which candidates are even worth testing.

4. **Point group matching.** The found set of symmetry elements is compared against a library of all known point groups, each defined by its required element counts. A scoring function finds the best-fitting group — the one whose requirements are most closely satisfied without contradiction.

5. **Axis assignment and labelling.** The Cartesian frame is standardised: z is set along the highest-order proper rotation axis, and x is chosen to pass through the greatest number of atoms in the xz plane. Mirror planes and C₂ axes are then labelled according to crystallographic convention (σₕ, σᵥ, σₐ, C₂′, etc.).

## Installation

**From PyPI (when published):**
```bash
pip install schoenflies-py
```

**From source:**
```bash
git clone https://gitlab.com/your-username/schoenflies-py.git
cd schoenflies-py
pip install -e .
```

**Dependencies** (installed automatically): `numpy`, `scipy`

## Usage

**Command line:**
```bash
python -m schoenflies molecule.xyz
```

Example output:
```
Molecule:   H2O (3 atoms)
Rotor type: Asymmetric Top
Symmetry elements found: E, C2, σv, σv'
Point group: C2v
```

**Python import:**
```python
from schoenflies import Molecule, SymmetryFinder, PointGroupClassifier

mol = Molecule("molecule.xyz")
finder = SymmetryFinder(mol)
elements = finder.find_all()
classifier = PointGroupClassifier(elements)
print(classifier.point_group)   # e.g. "C2v"
```

## Input format

The program accepts standard `.xyz` files:

```
5
Water molecule (H2O)          ← comment line (can be blank)
O   0.000000   0.000000   0.119748
H   0.000000   0.756950  -0.478993
H   0.000000  -0.756950  -0.478993
```

- Line 1: total number of atoms
- Line 2: comment (ignored by the parser)
- Lines 3+: element symbol followed by x, y, z coordinates in **Ångströms**

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
| Dihedral with σₐ | D₂ₐ, D₃ₐ, D₄ₐ, D₅ₐ, D₆ₐ |
| Cubic | Tₐ, T, Tₕ, O, Oₕ |
| Linear | C∞ᵥ, D∞ₕ |

## Known limitations

- **Tolerance sensitivity.** All geometry checks use a fixed tolerance of 0.02 Å. Molecules with near-symmetry (e.g. slightly distorted geometries from a relaxed scan) may be misclassified. This value can be adjusted in `utils.py`.
- **Maximum Cₙ order = 8.** Axes of order higher than 8 are not searched. This covers all chemically common cases but excludes exotic or hypothetical molecules with very high-order axes.
- **No periodic structures.** The algorithm operates on a single isolated molecule. Crystal structures, unit cells, and space groups are not supported.
- **Geometry must be a minimum or stationary point.** Arbitrary snapshots from a trajectory may have numerical noise that triggers false symmetry failures.

## References

- Johansson, M. P. & Veryazov, V. (2017). *Automatic procedure for generating symmetry adapted wavefunctions*. **Journal of Cheminformatics**, 9, 36. https://doi.org/10.1186/s13321-017-0193-3
- Original C++ implementation: https://gitlab.com/lkkmpn/schoenflies
