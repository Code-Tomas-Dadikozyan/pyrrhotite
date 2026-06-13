# CLAUDE.md — pyrrhotite (Schoenflies Point Group Determination)

## Project Goal
`pyrrhotite` is a Python implementation of Schoenflies point-group determination,
character-table generation, idealized-structure generation, and a 3-D molecule
visualizer. It began as a translation of the C++ library `schoenflies` by Luuk
Kempen (https://gitlab.com/lkkmpn/schoenflies) and has since diverged (notably:
on-the-fly character-table generation for any axial group, HTML/LaTeX export, and
a structure generator). The original C++ source was vendored under `reference/`
during the initial translation but was **removed in 0.2.0** — it is no longer in
this repository. Many module headers still cite the original C++ file they were
translated from, purely as provenance.

The package is an educational/reference codebase: code is expected to be heavily
and clearly commented for a learning audience.

## Repository Structure
```
pyrrhotite/
│
├── .claude/
│   ├── .claudeignore       ← Claude config. Do not modify.
│   └── CLAUDE.md           ← This file.
│
├── .github/                ← CI workflows (wheels, docs deploy).
├── .vscode/                ← Editor settings. Ignore.
├── docs/                   ← MkDocs site (Markdown + mkdocstrings api.md).
├── src/                    ← Primary working directory: the `pyrrhotite` package.
│   ├── symmetry.py             determination pipeline
│   ├── structure.py            XYZ loading / COM centering
│   ├── structure_generator.py  idealized-structure generation
│   ├── display.py              pretty-printers + sample-molecule helpers
│   ├── rotor_class.py          rotor classification enum
│   ├── periodic_table.py       element data
│   ├── operations/             symmetry-operation classes + manager
│   ├── point_groups/           PointGroup, labels, hardcoded groups, basis functions
│   ├── character_tables/       analytical generator + HTML/LaTeX formatters
│   ├── sample_molecules/       bundled `*.xyz` sample molecules (shipped in wheel)
│   └── visualizer/             PyQt6 + OpenGL viewer (optional `[vis]` extras)
├── tests/                  ← Test files (read samples from `src/sample_molecules/`).
│
├── example_usage.py        ← Runnable feature demo.
├── .gitignore              ← Do not modify.
├── CHANGELOG.md            ← Update when meaningful changes are made.
├── LICENSE                 ← Do not modify.
├── pyproject.toml          ← Do not modify unless explicitly instructed.
└── README.md               ← Do not modify unless explicitly instructed.
```

## Permissions

### You MAY
- Read any file in the repository
- Create and edit files inside `src/`, `tests/`, and `docs/`
- Run `pytest` and `python`
- Install packages explicitly listed under dependencies in `pyproject.toml`

### You MAY NOT
- Modify `pyproject.toml`, `.gitignore`, or `.claudeignore` unless explicitly asked
- Install packages not listed in `pyproject.toml` without asking first
- Refactor working, tested code unless explicitly instructed

## Coding Conventions
- Python 3.10+
- Type hints required on all function signatures
- NumPy arrays preferred over plain lists for numerical data
- Each module needs a header description; each function/class a docstring
  explaining its role in the algorithm
- For this educational codebase, comments should *teach* (explain the why /
  the maths), not merely restate the code
- Where a translated C++ idiom required a non-obvious Python equivalent, comment
  the location
- Source files are plain UTF-8 (no BOM)
