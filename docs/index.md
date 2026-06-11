<div class="pyrrhotite-hero" markdown>

# pyrrhotite

**Automatic Schoenflies point group determination, character table generation, and
3-D molecule visualization — from a plain `.xyz` file or from nothing at all.**

[Get started :material-arrow-right:](getting-started.md){ .md-button .md-button--primary }
[Read the user guide](user-guide.md){ .md-button }
[View on GitHub :fontawesome-brands-github:](https://github.com/Code-Tomas-Dadikozyan/pyrrhotite){ .md-button }

</div>

<div class="pyrrhotite-badges" markdown>
[![License: GPLv3](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://github.com/Code-Tomas-Dadikozyan/pyrrhotite/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](getting-started.md#installation)
![Status](https://img.shields.io/badge/status-active%20development-yellow.svg)
[![Schoenflies groups](https://img.shields.io/badge/point%20groups-18%20classes-d4a017.svg)](algorithm.md#supported-point-groups)
</div>

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

!!! tip "New to point groups?"
    If "Schoenflies symbol" and "character table" don't mean much to you yet,
    start with [What is a point group?](#what-is-a-point-group) below — it's a
    short primer on the chemistry behind what `pyrrhotite` computes.

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

!!! example "A quick mental model"
    Think of water (H₂O): it has a mirror plane through the O atom and both H
    atoms, another mirror plane perpendicular to it, and a 2-fold rotation axis
    where they meet. That combination of operations *is* the point group **C₂ᵥ**
    — and the character table for C₂ᵥ tells you, among other things, that water
    has three IR-active vibrational modes.

## What can pyrrhotite do?

<div class="grid cards" markdown>

-   :material-shape-outline: **Detect symmetry elements**

    ---

    Rotation axes, mirror planes, the inversion centre, and improper rotation
    axes — detected directly and numerically from atomic coordinates, no
    pre-classification needed.

-   :material-table: **Generate character tables**

    ---

    For any of the **18 Schoenflies classes**, including arbitrary-order
    C_n / C_nv / C_nh / S_n / D_n / D_nh / D_nd groups, with or without a
    structure.

-   :material-export: **Export to HTML or LaTeX**

    ---

    Turn character tables into ready-to-use HTML snippets or LaTeX tables for
    reports, slides, and web pages.

-   :material-rotate-3d-variant: **Visualize molecules in 3-D**

    ---

    An interactive viewer with colour-coded atoms, bonds, an orientation
    gizmo, and optional element labels.

-   :material-flask-outline: **Explore sample molecules**

    ---

    32 bundled `.xyz` files covering all major point-group families — water,
    ammonia, benzene, ferrocene, buckminsterfullerene, and more.

-   :material-cube-scan: **Generate idealized structures**

    ---

    Build a synthetic `.xyz` structure with a *requested* point-group symmetry
    — useful for testing, demos, and teaching.

</div>

!!! tip "Try it without installing anything yet"
    Every code example on this site uses the bundled sample molecules, so you
    can follow along the moment `pyrrhotite` is installed — no need to find or
    write your own `.xyz` files first. See
    [Sample molecules](user-guide.md#sample-molecules).

---

## Where this project came from

`pyrrhotite` started as a Python translation of the C++ library
[`schoenflies`](https://gitlab.com/lkkmpn/schoenflies) by Luuk Kempen, which
detects symmetry operations from an `.xyz` file and visualizes them on the
molecule. The two projects have since diverged — see [About](about.md) for the
full comparison and history.

!!! info "Why \"pyrrhotite\"?"
    Pyrrhotite is an iron sulfide mineral that crystallises into a range of
    related but distinct structures depending on composition and temperature —
    a fitting namesake for a library all about classifying structures by their
    symmetry.

---

## Explore the docs

<div class="grid cards" markdown>

-   :material-rocket-launch: **[Getting Started](getting-started.md)**

    ---

    Installation, optional extras, and a first analysis from the command line
    or Python.

-   :material-book-open-page-variant: **[User Guide](user-guide.md)**

    ---

    The full Python API: point groups, character tables, symmetry operations,
    basis functions, the 3-D viewer, and more.

-   :material-cog-outline: **[Algorithm & Supported Groups](algorithm.md)**

    ---

    How detection works under the hood, which point groups are supported, and
    known limitations.

-   :material-information-outline: **[About](about.md)**

    ---

    Project history, comparison with the original C++ tool, license,
    references, and contact info.

</div>

---

!!! warning "Work in progress"
    `pyrrhotite` is under active development — both the source code and these
    docs change frequently. If something here looks out of date compared to the
    [README](https://github.com/Code-Tomas-Dadikozyan/pyrrhotite#readme) or the
    code itself, the code is the source of truth. Found a discrepancy? See
    [About → Contact](about.md#contact) for how to report it.
