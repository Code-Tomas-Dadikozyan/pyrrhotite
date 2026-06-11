# pyrrhotite

**Automatic Schoenflies point group determination, character table generation, and
3-D molecule visualization — from a plain `.xyz` file or from nothing at all.**

Given a molecular geometry in `.xyz` format, `pyrrhotite` identifies the molecule's
Schoenflies point group symbol by numerically detecting all present symmetry
elements (rotations, reflections, inversions, and improper rotations), then builds
the full character table for that group — even for groups it has never seen before.

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

[Get started :material-arrow-right:](getting-started.md){ .md-button .md-button--primary }
[Read the user guide](user-guide.md){ .md-button }

---

## What is a point group?

A **point group** is the complete set of symmetry operations that leave a
molecule's geometry unchanged. Every molecule belongs to exactly one point group,
and its label (e.g. C₂ᵥ, D₆ₕ, T_d, O_h) encodes its full symmetry in compact
notation.

Point group symmetry determines which molecular orbitals can mix, which
vibrational modes are IR- or Raman-active, and how a molecule interacts with
polarised light. The **character table** of a point group is the lookup table
that encodes all of this.

## What can pyrrhotite do?

- :material-shape-outline: **Detect symmetry elements** — rotation axes, mirror
  planes, the inversion centre, and improper rotation axes — directly from atomic
  coordinates.
- :material-table: **Generate character tables** for any of the 18 Schoenflies
  classes, including arbitrary-order C_n / C_nv / C_nh / S_n / D_n / D_nh / D_nd
  groups, with or without a structure.
- :material-export: **Export character tables** to HTML or LaTeX for reports,
  slides, and web pages.
- :material-rotate-3d-variant: **Visualize molecules** in an interactive 3-D
  viewer with an orientation gizmo and optional element labels.
- :material-flask-outline: **Explore 32 bundled sample molecules** covering all
  major point-group families — water, ammonia, benzene, ferrocene,
  buckminsterfullerene, and more.

## Where this project came from

`pyrrhotite` started as a Python translation of the C++ library
[`schoenflies`](https://gitlab.com/lkkmpn/schoenflies) by Luuk Kempen, which
detects symmetry operations from an `.xyz` file and visualizes them on the
molecule. The two projects have since diverged — see [About](about.md) for the
full comparison and history.

---

## Quick links

| | |
|---|---|
| :material-rocket-launch: [**Getting Started**](getting-started.md) | Installation and a first analysis |
| :material-book-open-page-variant: [**User Guide**](user-guide.md) | The Python API and command-line tool in depth |
| :material-cog-outline: [**Algorithm & Supported Groups**](algorithm.md) | How detection works, and what's supported |
| :material-information-outline: [**About**](about.md) | Project history, references, and license |

!!! note "Work in progress"
    `pyrrhotite` is under active development — both the source code and these
    docs change frequently. If something here looks out of date compared to the
    [README](https://github.com/Code-Tomas-Dadikozyan/pyrrhotite#readme) or the
    code itself, the code is the source of truth.
