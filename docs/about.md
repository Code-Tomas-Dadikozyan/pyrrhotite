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
python -m pytest tests/ -v
```

See the project's
[CHANGELOG](https://github.com/Code-Tomas-Dadikozyan/pyrrhotite/blob/main/CHANGELOG.md)
for a history of recent changes.
