# About

## Where this project came from

`pyrrhotite` started as a Python translation of the C++ library
[`schoenflies`](https://gitlab.com/lkkmpn/schoenflies) by Luuk Kempen, which
detects symmetry operations from an `.xyz` file and visualizes them on the
molecule.

The two projects have since diverged:

| | Luuk Kempen's `schoenflies` (C++) | `pyrrhotite` (this project) |
|---|---|---|
| Point group determination from `.xyz` | ✅ | ✅ |
| Character table generation | ❌ | ✅ — for **any** of the 18 Schoenflies classes, including arbitrary order Cₙ groups, with or without an `.xyz` file |
| HTML / LaTeX export of character tables | ❌ | ✅ |
| 3-D visualizer | ✅ — shows the molecule **and overlays the detected symmetry operations** (axes, planes) | ✅ — shows the molecule with an orientation gizmo and optional element labels (symmetry-operation overlays are not yet implemented) |
| Sample molecule library | ❌ | ✅ — 32 bundled `.xyz` files with one-line helpers |

In short: if you need to *see* the symmetry operations drawn on a molecule, the
original C++ tool is currently the better choice. If you need character
tables — generated on demand for any point group, with or without a structure —
`pyrrhotite` is the tool for that.

---

## Citing this work

!!! example "If pyrrhotite is useful in your research or coursework"
    There isn't a dedicated paper for `pyrrhotite` itself yet — please cite
    the original `schoenflies` project and the symmetry-adapted wavefunction
    reference below, and link back to the
    [GitHub repository](https://github.com/Code-Tomas-Dadikozyan/pyrrhotite).

---

## License

`pyrrhotite` is released under the GNU General Public License v3.0 — see
[LICENSE](https://github.com/Code-Tomas-Dadikozyan/pyrrhotite/blob/main/LICENSE)
for details.

---

## References

- Original C++ implementation by Luuk Kempen:
  [gitlab.com/lkkmpn/schoenflies](https://gitlab.com/lkkmpn/schoenflies)
- Johansson, M. P. & Veryazov, V. (2017). *Automatic procedure for generating
  symmetry adapted wavefunctions*. **Journal of Cheminformatics**, 9, 36.
  [doi.org/10.1186/s13321-017-0193-3](https://doi.org/10.1186/s13321-017-0193-3)

---

## Contributing & development

Running the test suite:

```bash
pip install 'pyrrhotite[dev]'
python -m pytest tests/ -v
```

!!! tip "Keep an eye on the changelog"
    `pyrrhotite` is under active development. See the project's
    [CHANGELOG](https://github.com/Code-Tomas-Dadikozyan/pyrrhotite/blob/main/CHANGELOG.md)
    for a history of recent changes — useful context if something here
    doesn't quite match the installed version.

---

## Contact

Questions, bug reports, and feature requests are all welcome:

<div class="grid cards" markdown>

-   :fontawesome-brands-github: **GitHub Issues**

    ---

    Found a bug, or detection giving an unexpected point group? Open an issue
    with the `.xyz` file (or a minimal reproduction) on the
    [issue tracker](https://github.com/Code-Tomas-Dadikozyan/pyrrhotite/issues).

-   :material-source-repository: **Source code**

    ---

    Browse the code, open a pull request, or fork the project on
    [GitHub](https://github.com/Code-Tomas-Dadikozyan/pyrrhotite).

-   :material-email-outline: **Email**

    ---

    For anything that doesn't fit a public issue, reach the maintainer at
    [tdadikozyan04@gmail.com](mailto:tdadikozyan04@gmail.com).

</div>
