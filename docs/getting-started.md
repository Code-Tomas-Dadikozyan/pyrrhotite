# Getting Started

## Installation

```bash
pip install pyrrhotite
```

**Requirements:** Python 3.10+

!!! tip "Use a virtual environment"
    As with any Python package, it's good practice to install `pyrrhotite`
    into a virtual environment rather than your system Python:

    ```bash
    python -m venv .venv
    source .venv/bin/activate    # on Windows: .venv\Scripts\activate
    pip install pyrrhotite
    ```

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

!!! warning "PyQt6 and OpenGL need system libraries on Linux"
    On Linux, `PyQt6` and `PyOpenGL` may additionally require system packages
    (e.g. Qt6 platform plugins and a working OpenGL/EGL/X11 stack) that `pip`
    cannot install for you. If `visualize()` fails to open a window, check
    your distribution's Qt6/OpenGL packages first — the Python packages
    themselves installed correctly.

For development (running the test suite):

```bash
pip install 'pyrrhotite[dev]'   # installs pytest
```

??? question "Common installation issues"
    **`ModuleNotFoundError: No module named 'pyrrhotite'` right after installing**
    : Check that the virtual environment you installed into is the one your
      shell or IDE is actually using (`python -m pip show pyrrhotite` should
      print a location). This is the most common cause when `pip install` and
      `python` are picking up different environments.

    **`pip install 'pyrrhotite[vis]'` fails to build `PyOpenGL` or `PyQt6`**
    : These ship prebuilt wheels for all common platforms; a build-from-source
      attempt usually means `pip` itself is outdated. Try
      `python -m pip install --upgrade pip` first, then re-run the install.

    **The 3-D viewer opens but is blank, or `visualize()` raises immediately on Linux**
    : See the note above about Qt6/OpenGL system packages — the Python side
      installed correctly, but the platform plugin or OpenGL driver is
      missing.

    **Still stuck?** See [About → Contact](about.md#contact).

---

## Quick start

=== "Python"

    ```python
    from pyrrhotite import Structure, Symmetry

    s = Structure("molecule.xyz")
    sym = Symmetry(s)

    print(sym.point_group.label.name)   # e.g. "C3v"
    ```

=== "Command line"

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

!!! note "Units and precision"
    Coordinates are assumed to be in **Ångströms**. Symmetry detection uses a
    tolerance of 10% of the distance to the candidate symmetry element, so
    typical 3-4 decimal-place `.xyz` files are more than precise enough — see
    [Algorithm & Supported Groups](algorithm.md) for details on how tolerances
    affect detection of high-order axes.

---

## Command-line reference

```bash
pyrrhotite molecule.xyz
pyrrhotite src/sample_molecules/*.xyz

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

!!! tip "Scripting and CI"
    Pass `--plain` whenever output is going somewhere other than an
    interactive terminal (CI logs, files, piping into other tools) — it
    disables `rich`'s colour/box-drawing output so the result is plain,
    grep-friendly text. Several `-` flags can also be combined, e.g.
    `pyrrhotite -v -ct -m -od ammonia.xyz` runs every analysis at once.

---

## Next steps

- Walk through the full Python API in the [User Guide](user-guide.md).
- Learn how detection works and what's supported in
  [Algorithm & Supported Groups](algorithm.md).

??? question "Something not working as expected?"
    Double-check the [Input format](#input-format) above (units, file
    structure), and see [About → Contact](about.md#contact) if you'd like to
    report a bug or ask a question.
