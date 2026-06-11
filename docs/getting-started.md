# Getting Started

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

### Optional extras

The 3-D visualizer needs extra graphics libraries that aren't installed by
default:

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

### Python

```python
from pyrrhotite import Structure, Symmetry

s = Structure("molecule.xyz")
sym = Symmetry(s)

print(sym.point_group.label.name)   # e.g. "C3v"
```

### Command line

```bash
pyrrhotite molecule.xyz
pyrrhotite -v -ct ammonia.xyz   # verbose + character table
```

---

## Input format

`pyrrhotite` reads standard `.xyz` files (coordinates in Ångströms):

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

## Command-line reference

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

### Example output

`pyrrhotite -v -ct --plain ammonia.xyz`:

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

## Next steps

- Walk through the full Python API in the [User Guide](user-guide.md).
- Learn how detection works and what's supported in
  [Algorithm & Supported Groups](algorithm.md).
