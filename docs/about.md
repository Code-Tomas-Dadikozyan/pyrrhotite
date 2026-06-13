# About

## Where this project came from

`pyrrhotite` started as a Python translation of the C++ library
[`schoenflies`](https://gitlab.com/lkkmpn/schoenflies) by Luuk Kempen, which
detects symmetry operations from an `.xyz` file and visualizes them on the
molecule.

The two projects have since diverged:

| Feature | `schoenflies` (C++) | `pyrrhotite` |
|---|---|---|
| Point group determination from `.xyz` | ✅ | ✅ |
| Character tables | ❌ | ✅ — generated for any of the 18 Schoenflies classes (axial families to arbitrary order), with or without an `.xyz` file, and exportable to HTML / LaTeX |
| Idealized structure generation | ❌ | ✅ — build a molecule that has a requested axial symmetry, for testing or demonstration |
| 3-D visualizer | ✅ — overlays the detected symmetry operations (axes, planes) on the molecule | ✅ — molecule, axis gizmo, and optional element labels (no operation overlays yet) |
| Sample molecule library | ❌ | ✅ — 32 bundled `.xyz` files with one-line helpers |

In short: reach for the original C++ tool if you need to *see* the symmetry
operations drawn on a molecule. Reach for `pyrrhotite` if you need character
tables — on demand for any point group, with or without a structure — or any of
the other features above.

---

## Citing this work

!!! example "If pyrrhotite is useful in your research or coursework"
    There isn't a dedicated paper for `pyrrhotite` itself yet — please cite
    the original `schoenflies` project and the symmetry-adapted wavefunction
    reference below, and link back to the
    [GitHub repository](https://github.com/datomic117/pyrrhotite).

---

## License

`pyrrhotite` is released under the GNU General Public License v3.0 — see
[LICENSE](https://github.com/datomic117/pyrrhotite/blob/main/LICENSE)
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
    [CHANGELOG](https://github.com/datomic117/pyrrhotite/blob/main/CHANGELOG.md)
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
    [issue tracker](https://github.com/datomic117/pyrrhotite/issues).

-   :material-source-repository: **Source code**

    ---

    Browse the code, open a pull request, or fork the project on
    [GitHub](https://github.com/datomic117/pyrrhotite).

-   :material-email-outline: **Email**

    ---

    For anything that doesn't fit a public issue, reach the maintainer at
    [tdadikozyan04@gmail.com](mailto:tdadikozyan04@gmail.com).

</div>
