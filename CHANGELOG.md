# Changelog

All notable changes to this project will be documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.0] - 2026-06-10

### Added
- `src/visualizer/` — interactive 3-D molecule viewer built on PyQt6 and OpenGL. Atoms are drawn as spheres (coloured per element from `periodic_table.py`), bonds as cylinders, with an orientation gizmo (red/green/blue arrows for x/y/z) and an optional element-symbol overlay. Controls: left-drag to rotate (arcball), scroll to zoom. Exposed as `pyrrhotite.visualize(structure, show_labels=False)`.
- New optional install extra `pip install 'pyrrhotite[vis]'` (PyQt6, PyOpenGL, pyrr, matplotlib) for the visualizer.
- New CLI flags `--visualize`/`-vis` (open the 3-D viewer after analysis) and `--labels`/`-l` (show element labels in the viewer; implies `--visualize`).
- `src/display.py` — pretty-printing helpers (`print_bond_pairs`, `print_ops_with_atoms`, `print_basis_functions`, `print_char_table_programmatic`) and sample-molecule convenience functions (`list_sample_molecules`, `load_sample`, `analyse_sample`, `visualize_sample`, `show_character_table_sample`) built on the bundled `tests/files/` molecules. All re-exported from the top-level `pyrrhotite` package.
- `src/character_tables/` — character table generation split out into its own subpackage:
  - `generator.py` (moved from `src/point_groups/character_table_generator.py`)
  - `html_formatter.py` — `format_html()` / `save_html()`, render character tables as standalone HTML
  - `latex_formatter.py` — `format_latex()` / `save_latex()`, render character tables as LaTeX (requires the `booktabs` and `amsmath` packages)

### Changed
- Character table generation now lives under `src/character_tables/` instead of `src/point_groups/character_table_generator.py`; `parse_point_group_name`, `generate_point_group`, `get_or_generate_point_group`, and `print_character_table_for` are imported from `src.character_tables`.

### Removed
- The vendored C++ reference implementation (`reference/`) has been removed from the repository. The original project remains available at https://gitlab.com/lkkmpn/schoenflies.

## [0.1.0] - 2026-05-11

### Added
- Full Python translation of the Schoenflies point group determination algorithm from the C++ reference implementation (originally vendored under `reference/src/`; removed from the repository in 0.2.0 — see https://gitlab.com/lkkmpn/schoenflies for the original)
- `src/periodic_table.py` — hardcoded atomic data (symbol, mass, covalent radius, colour) for all 118 elements, translated from the C++ reference's `periodic_table/periodic_table.cpp`
- `src/rotor_class.py` — `RotorClass` enum (AsymmetricTop, OblateSymmetricTop, ProlateSymmetricTop, Linear, SphericalTop)
- `src/structure.py` — `Structure` class: XYZ file loading, centre-of-mass centering, closest-atom lookup, bond-pair detection
- `src/operations/operation_label.py` — `OperationLabel` with inner `Element`, `Plane`, and `Prime` enums; factory classmethods mirroring C++ overloaded constructors
- `src/operations/operation_label_count.py` — `OperationLabelCount` pairing a label with a multiplicity count
- `src/operations/operation_group.py` — `OperationGroup` grouping operation IDs under a shared label
- `src/operations/operation.py` — `Operation` class: Rodrigues rotation matrices, Householder reflection matrices, inversion, improper rotation; `do_operation` atom-mapping with normalised error metric
- `src/operations/operation_manager.py` — `OperationManager`: validates, deduplicates, and stores found operations; generates the final labelled point-group operation set
- `src/point_groups/irrep_label.py` — `IrrepLabel` with `Mulliken`, `Parity`, and `Prime` enums for Mulliken notation
- `src/point_groups/point_group_label.py` — `PointGroupLabel` with `Class` enum covering all 18 point-group families including C∞v and D∞h
- `src/point_groups/point_group.py` — `PointGroup` class with `compare_to_symmetry_operations` used by the matching algorithm
- `src/point_groups/point_groups.py` — hardcoded definitions for all 54+ point groups with operation counts, irreducible representations, and character tables
- `src/symmetry.py` — `Symmetry` class: full 7-step pipeline (principal axes via inertia tensor, rotor classification, symmetry-operation search, point-group matching, Cartesian axis assignment, operation labelling, point-group operation generation)
- `tests/files/` — 32 XYZ test molecules copied from `reference/test/files/` covering all major point-group families
- `tests/conftest.py` — pytest fixtures and expected point-group label mapping for all 32 molecules
- `tests/test_structure.py` — unit tests for XYZ loading, COM centering, `find_closest_index`, and `calculate_bond_pairs`

## [0.1.1] - 2026-06-03

### Added
- `src/point_groups/character_table_generator.py` — automatic character table generator for all seven axial point group families (Cn, Cnh, Cnv, Sn, Dn, Dnh, Dnd) for arbitrary order n ≥ 2, implementing the analytical formulas from Johansson & Veryazov (2017). Exposes `generate_point_group(label)` and `get_or_generate_point_group(label)`. (Moved to `src/character_tables/generator.py` in 0.2.0.)
- `Symmetry._generate_point_group_from_ops` fallback in `_find_point_group`: when no hardcoded group matches the detected operations (e.g. n > 10), the family and order are inferred and the table is generated on-the-fly.
- `tests/test_character_table_generator.py` — 120 tests: consistency against all hardcoded axial tables, off-diagonal row orthogonality for n > 10, structural sanity checks, and spot-checks of known analytical values.

### Fixed
- `testversion.py` was reading `pyrrhotite/_version.py` instead of `src/_version.py`, causing the CI version-check job to fail (`FileNotFoundError`)
- `testversion.py` was also attempting to open `meta.yaml`, which does not exist in the repository; the `meta.yaml` check has been removed


## [0.1.2] - 2026-06-03


### Added
- PyPI long description: `README.md` rewritten for the project page — `pip install pyrrhotite` install instructions, quick-start example, full CLI flag reference, and example output