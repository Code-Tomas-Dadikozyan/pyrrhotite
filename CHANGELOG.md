# Changelog

All notable changes to this project will be documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.2] - 2026-06-13

### Fixed
- Documentation site footer: the "Contact the maintainer" envelope icon used a
  relative link (`about/#contact`) which, since MkDocs does not rewrite social
  links, resolved relative to the current page and produced a broken doubled URL
  (e.g. `.../pyrrhotite/about/about/#contact`). It now uses the absolute site URL.
  A `site_url` was also added to `mkdocs.yml` (previously missing) so Material can
  generate correct canonical/absolute links.
- `docs/index.md`: the "Why pyrrhotite?" admonition title escaped its inner
  double-quotes as `\"`, which rendered the literal backslashes on the site. It
  now uses typographic curly quotes so it renders cleanly.
- `README.md`: the two `example_usage.py` links were repository-relative, so they
  worked on GitHub but 404'd on the rendered PyPI project page. They are now
  absolute GitHub URLs that resolve everywhere the README is shown. The Quick-start
  blockquote also now clarifies that the script ships with the repository rather
  than the installed wheel, and points to the new docs page below.

### Documentation
- Added a new "Example Script" page (`docs/example.md`) that embeds the full
  `example_usage.py` inline via `pymdownx.snippets` (kept in sync with the real
  file on every build) alongside a view/download-on-GitHub link, so the showcase
  is readable directly on the docs site without leaving it. Added to the Guide
  navigation and cross-linked from the User Guide intro.

## [0.2.1] - 2026-06-12

### Fixed
- `Symmetry._find_point_group` no longer silently mis-identifies molecules whose
  detected proper-rotation order exceeds the hardcoded group range. Previously a
  genuine high-order axis (e.g. a detected C11) could still match a low-order
  hardcoded group such as D2h with a non-negative operation surplus and win,
  because the analytical fallback only ran when *no* hardcoded group matched at
  all. A hardcoded group is now accepted only if it can account for the
  highest-order proper axis actually detected (new `Symmetry._group_accounts_for_axis`
  / `PointGroup.num_proper_rotations`); otherwise the analytical generator is used.
- `Symmetry._generate_point_group_from_ops` (the analytical fallback) was reading
  reflection-plane σh/σv/σd labels that are not assigned until *after* point-group
  determination, so its plane tests were always False — it could never produce a
  Dnd group and misclassified Cnh/Dnh/Dnd. It now derives horizontal-vs-vertical
  planes geometrically from each plane's normal relative to the principal axis
  (the same criterion the labeller uses), correctly distinguishing Dnh (has σh)
  from Dnd (only σd), and uses the improper-rotation order for the Sn label.
  Net effect: the Cn/Cnh/Cnv/Dn/Dnh/Dnd families now round-trip correctly through
  generate-then-detect for the full adaptive range n = 3–20 (previously only the
  n ≤ 10 cases covered by the test suite were reliable).
- Narrowed an overly broad `except (ValueError, Exception)` in the same fallback
  to `except ValueError`, so unexpected errors are no longer silently swallowed.
- `Symmetry._find_point_group` now also requires a candidate hardcoded group to
  account for the highest-order *improper* (Sₙ) axis detected, not just the
  highest proper axis (new `Symmetry._max_finite_degree` /
  `_group_accounts_for_axes`, plus `PointGroup.num_improper_rotations`). This
  fixes two high-order mis-detections: an Sₙ molecule (which contains the proper
  rotation C_{n/2}) was matching a hardcoded C_{n/2} and hiding its Sₙ axis
  (e.g. S12 → C6), and a genuine D8d — whose S16 class is under-counted by the
  operation search — was losing to C8v. Both now fall through to the analytical
  generator and resolve correctly. All seven axial families now round-trip
  through generate-then-detect for the full adaptive range (Cn/Cnh/Cnv/Dn/Dnh/Dnd
  n = 3–20, Sn n = 4–20).
- `generate_idealized_structure`: for the Dn/Dnh/Dnd and Sn families the ring
  radius is now capped so the central hub stays within bonding distance of every
  ring atom regardless of n. Previously `_radius_for(n)` grew ~linearly with n,
  so for larger structures (e.g. D20h) the rings drifted beyond the hub-ring
  bonding cutoff and the hub rendered as an unconnected atom floating between the
  two rings in the 3-D viewer (new `_hub_bonded_ring_radius` helper). Hub-ring
  bonding is verified for all of Dn/Dnh/Dnd/Sn through n = 20.
- `list_sample_molecules` (and the other `*_sample` helpers in `display.py`) raised
  `FileNotFoundError: .../site-packages/tests/files` when called from a pip-installed
  package, because the sample XYZ files lived only in the repo's `tests/files/`
  directory, which is not shipped in the wheel. The sample molecules now live inside
  the package at `pyrrhotite/sample_molecules/` (declared as package-data in
  `pyproject.toml`) as the single source of truth: `display.py` resolves them there,
  and the test suite's `XYZ_DIR` was repointed to the same directory, so the old
  `tests/files/` directory has been removed.
- `generate_idealized_structure`: ring atoms no longer visually crowd ("smush")
  together at high orders. The central hub now uses caesium (the largest covalent
  radius in `periodic_table.py`, raised to its true Alvarez-2008 value of 2.44 Å)
  instead of iron; the wider hub-ring bonding cutoff lets the rings sit at a larger
  radius while the hub still bonds to every ring atom, so adjacent ring atoms stay
  comfortably separated through n = 20 (e.g. minimum atom spacing in D20h rose from
  ~0.87 Å to ~1.28 Å, versus a ~0.8 Å rendered sphere diameter).
- `generate_idealized_structure`: the central hub element for the Dn/Dnh/Dnd and
  Sn families is now chosen dynamically by ring size instead of always being
  caesium. A fixed Cs hub (covalent radius 2.44 Å) is right for large n — its
  wide bonding cutoff lets far-out rings stay connected — but at small n the
  rings sit only ~2 Å from the centre, so the 2.44 Å hub sphere visually engulfed
  them in the 3-D viewer. `_hub_element_for` now picks the smallest hub that
  still bonds to the ring at its natural radius (Cl → Fe → Cs), so small
  structures get a small hub and only large orders escalate to caesium. The hub
  still bonds to every ring atom and all seven axial families round-trip through
  detection across n = 3–20 (Sn 4–20).

### Documentation
- Simplified the `pyrrhotite`-vs-`schoenflies` comparison table in `README.md` and
  `docs/about.md`: folded the HTML/LaTeX export row into a single "Character tables"
  row and added an "Idealized structure generation" row reflecting that feature.
- `README.md` polish: added PyPI/Python/license/docs badges, a name-origin note,
  a linked table of contents, a documentation-site pointer, a 3-D viewer screenshot
  (`docs/assets/visualizer-fullerene.png`), a rendered LaTeX export example, and cross-links
  to the User Guide / Algorithm pages. Consolidated the "viewer does not draw
  symmetry overlays yet" caveat to a single canonical spot, and fixed the stale
  `tests/files/*.xyz` CLI example to `src/sample_molecules/*.xyz`.
- Added a disclaimer to the idealized-structure-generator section (`README.md` and
  `docs/user-guide.md`) clarifying that it only illustrates a point group's
  geometry — element and bond choices are for visualization only and do not
  represent real chemical structures — and documenting the supported families
  (no `Dnv`; only `Dnh`/`Dnd`) and the high-`n` rendering/detection limits (n ≤ 20).
- Added docstrings to previously undocumented helpers across the codebase: the
  10 internal row-builders in `character_tables/generator.py`, the visualizer's
  Qt/OpenGL override methods (`gl_widget`, `shader_program`, `model_manager`,
  `structure_renderer`, `window`, `obj_loader`), nested helpers in `symmetry.py`,
  `display.py`, `operation_manager.py`, and `basis_functions.py`, and module
  docstrings for the `visualizer/models` and `visualizer/shaders` packages.
- Added teaching notes in `symmetry.py` explaining the deliberately permissive
  asymmetric-top inertial filter and the scale-dependent absolute thresholds used
  for linearity/planarity.
- Reworded stale "Direct translation of reference/…" / "Mirrors reference/…"
  module headers to note that the vendored `reference/` tree was removed in 0.2.0.
- `README.md`: documented that improper-axis families (Sₙ, and the S₂ₙ axis of
  Dₙd) detect reliably only to ~n = 10, while the proper-axis families now detect
  across the full n = 3–20 adaptive range.
- Added a "Detecting high-order axes (n > 10)" explainer to both `README.md` and
  `docs/algorithm.md` covering the three mechanisms that lift the cap from n ≤ 8
  to n = 20 (geometry-bounded search order via `_max_plausible_order`, the
  order-dependent validation tolerance `min(0.1, π/(degree·(degree+1)))`, and
  matching that respects the highest detected proper/improper axis), plus an
  assessment of whether the fixed 10% tolerance is problematic.
- `docs/stylesheets/extra.css`: the Mermaid flowcharts on the User Guide and
  Algorithm pages now fill their nodes with the brand amber on navy (matching the
  "Get started" button) instead of a faint 10%-opacity wash; and the home-page
  navigation cards whose title is a link are now clickable across the whole card
  (a stretched-link `::after` overlay), scoped so multi-link cards like the About
  page's Contact cards are unaffected.
- `docs/api.md`: added `structure_generator.format_xyz`, plus a new "Display
  helpers" section documenting the four `pyrrhotite.display` pretty-printers
  (`print_bond_pairs`, `print_ops_with_atoms`, `print_basis_functions`,
  `print_char_table_programmatic`), which were previously undocumented.
- Documented the `pyrrhotite.display` pretty-printers in `README.md` and
  `docs/user-guide.md` as well, and surfaced the runnable `example_usage.py`
  feature tour (previously only referenced in passing) in the README Quick start
  and the User Guide intro.
- `example_usage.py`: the showcase now loads its demo molecules via the bundled
  `load_sample(...)` helper instead of hard-coded `tests\files\*.xyz` paths,
  which no longer exist (samples moved into the package in 0.2.1) and were
  Windows-only backslash paths — so the script now runs as-is on any platform
  straight after `pip install pyrrhotite`.
- `.claude/CLAUDE.md`: rewritten to describe the actual `src/` package layout
  (the file still referenced the obsolete `schoenflies/` + `reference/` layout).
- Source files normalised to plain UTF-8 (BOM removed).

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
- `src/structure_generator.py` — `generate_idealized_structure(point_group, ...)` builds an idealized `Structure` (rings of placeholder atoms) for any of the seven axial point groups (Cn, Cnh, Cnv, Sn, Dn, Dnh, Dnd) and order n, round-tripping through `Symmetry` to recover the same label. Also adds `format_xyz()` / `write_xyz()` for serialising the result to XYZ. Exposed via `pyrrhotite.generate_idealized_structure` / `pyrrhotite.write_xyz`, and via the CLI as `pyrrhotite -g <NAME> --xyz [PATH]`.
- `pyrrhotite.visualize_idealized_structure(point_group, ...)` — generates an idealized structure and opens the 3-D viewer directly, without writing it to an `.xyz` file first (requires `pip install 'pyrrhotite[vis]'`). Also available from the CLI as `pyrrhotite -g <NAME> --visualize` (or `--labels`/`-l`), when not combined with `--xyz`.
- `tests/test_structure_generator.py` — round-trip tests for `generate_idealized_structure` across all seven axial families and orders n=3..10 (including n>8 to exercise the adaptive axis-order search), plus error-path tests for unsupported families/orders.
- `example_usage.py` — new section 14 demonstrating `generate_idealized_structure`, `format_xyz`, and `write_xyz`: basic generation and round-trip detection, saving/reloading from disk, round-tripping all seven axial families at n=6, customising radius/height/element, and the error cases for unsupported groups/orders.

### Changed
- Character table generation now lives under `src/character_tables/` instead of `src/point_groups/character_table_generator.py`; `parse_point_group_name`, `generate_point_group`, `get_or_generate_point_group`, and `print_character_table_for` are imported from `src.character_tables`.
- Symmetry **detection** (`src/symmetry.py`) no longer caps proper-rotation search at Cn, n<=8. The three candidate-axis search functions (`_find_proper_rotational_axes_along_principal_axes`, `_find_proper_rotational_axes_through_atoms`, `_find_proper_rotational_axes_between_atoms`) now use a new `_max_plausible_order` helper, which derives a per-axis upper bound (capped at n=20) from the size of the largest ring of symmetry-equivalent atoms (same element, distance from axis, and position along axis) found around that axis.
- `src/operations/operation_manager.py`: the operation-validity tolerance is now tightened for high-order Cn/Sn candidates (degree >= 8), to `min(0.1, pi / (degree * (degree + 1)))`. This prevents a high-order axis (e.g. genuine C9) from also spuriously validating a neighbouring wrong-order candidate (e.g. C8), whose angular spacing would otherwise fall within the original fixed 0.1 tolerance.
- `find_point_group`, `get_or_generate_point_group`, and `generate_point_group` now accept either a `PointGroupLabel` or a Schoenflies name string (e.g. `"D6h"`), parsing the string internally via `parse_point_group_name`. Callers no longer need to write `find_point_group(parse_point_group_name("D6h"))` — `find_point_group("D6h")` is now sufficient.

### Fixed
- `generate_idealized_structure`'s default `radius`/`height` (now 1.0 A / 0.6 A, previously 1.5 A / 1.0 A) were too large relative to `Structure.calculate_bond_pairs`'s bonding cutoff for the placeholder element, leaving e.g. the two rings of a generated D9d structure as disconnected components with no bonds between them. The new defaults keep both within-ring and (for Dn/Dnd) cross-ring atoms within bonding distance, so generated structures render as connected molecules in the 3-D viewer, while still round-tripping correctly through `Symmetry`.
- `generate_idealized_structure`'s geometry has been redesigned per family so that `calculate_bond_pairs` produces realistic bonding patterns modelled on real molecules of the same point group, rather than over-connected uniform rings (previously every ring atom could end up bonded to ~4 neighbours, including spurious cross-ring bonds between otherwise unrelated rings):
  - **Cnv**: the ring is now sized so its atoms stay *outside* bonding distance of each other (like ammonia's H...H, which doesn't bond), while the apex atom remains within bonding distance of every ring atom. Each ring atom bonds only to the apex (degree 1); the apex bonds to all n ring atoms (degree n).
  - **Cn / Cnh**: the previous offset second ring (which could bond to multiple ring1 atoms, or to both an above and below decoration ring) is replaced by a single terminal-substituent atom per ring1 atom (like benzene's ring + H), giving each main-ring atom degree 3 (2 ring neighbours + 1 terminal atom) and each terminal atom degree 1.
  - **Dn / Dnh / Dnd**: now built around a central "hub" atom (a larger-radius placeholder element, e.g. Fe), mirroring ferrocene's metal-sandwich structure (`ferrocene-eclipsed.xyz` / `ferrocene-staggered.xyz`). The two rings are separated far enough that they no longer bond directly to each other; each is connected to the structure only via the hub. Each ring atom now has degree 3 (2 ring neighbours + hub) instead of 4.
  - **Sn**: also gains a central hub atom connecting the two halves of the antiprism (no more direct cross-ring bonds), with the existing Sn-symmetry-breaking "marker" atoms repositioned to bond as terminal substituents.
  - All seven families, n=3..10 (Sn even n=4..10), were verified to produce a single connected component, no near-zero-length bonds, and correct round-trip detection through `Symmetry`.
- `generate_idealized_structure`'s `Cn` family placed its terminal substituent atoms too close to their parent ring atom (bond length ~0.47 A, less than the sum of the two atoms' covalent radii), so the bond cylinder was completely hidden inside the overlapping atom spheres in the 3-D viewer. Each terminal atom is now placed at a fixed offset (~1 A) from its parent ring atom in that atom's local radial/tangential/z frame, giving a bond length comparable to the other families (and to a real C-H/N-H bond) regardless of `n`.
- `generate_idealized_structure`'s placeholder elements are now chosen to look like more plausible molecules: a new `_element_for_degree` helper maps each atom's designed bonding degree to an element with a roughly matching valence (H for degree 1, O for degree 2, N for degree 3, C for degree 4, S for degree 5-6, and a metal-like "Fe" hub for degree >= 7, consistent with the existing ferrocene-hub motif). At the default `element="F"`, the primary ring element for each family is substituted accordingly via `_ring_element` (e.g. "N" for the degree-3 ring atoms in Cn/Cnh/Dn/Dnh/Dnd, "C" for the degree-4 ring atoms in Sn, "H" for the now degree-1 ring atoms in Cnv, with the Cnv apex element chosen by its degree n). Since F, N, O, and C all share the same covalent radius (0.4 A), this is purely a cosmetic relabelling for those cases and does not change any bonding distances.
- `generate_idealized_structure`'s `Cnv` ring radius (previously sized purely from the ring-ring *unbonding* distance with a fixed margin) could, for `n >= 12`, end up larger than the apex-ring bonding cutoff itself, leaving the apex bonded to *no* ring atoms at all (an isolated apex floating in the centre of an unbonded ring, with zero visible bonds in the 3-D viewer). The ring radius is now sized as a fixed fraction of the apex-ring bonding cutoff instead, so the apex always bonds to every ring atom regardless of `n`; for `n <= 12` this still leaves ring atoms unbonded to each other (ammonia-like, degree 1), while for `n >= 13` neighbouring ring atoms also end up bonded (degree 3: 2 ring neighbours + apex) -- both patterns are connected and render with visible bonds.
- `generate_idealized_structure`'s `Cn` terminal-substituent offset's tangential component (0.4 A) could, for `n >= 12`, place the substituent within bonding distance of the *neighbouring* ring1 atom as well as its own (since ring1's nearest-neighbour spacing shrinks towards ~1.35 A as `n` grows), giving ring1 atoms degree 4 and substituents degree 2 instead of the intended benzene-like degree 3 / degree 1. The tangential component is now 0.2 A, which keeps the substituent bonded only to its own ring1 atom for all `n` up to 20.

### Removed
- The vendored C++ reference implementation (`reference/`) has been removed from the repository. The original project remains available at https://gitlab.com/lkkmpn/schoenflies.

### Documentation
- `src/symmetry.py` (`Symmetry._MAX_AXIS_ORDER`) and the README "Known limitations" section now explain why the n=20 adaptive-search cap can't simply be raised further: the per-degree validation tolerance shrinks roughly as 1/n^2 and approaches typical `.xyz` coordinate precision beyond n~20, detecting Cn still requires an actual n-fold ring of equivalent atoms in the molecule, and the ring-grouping search is O(atoms^2) per candidate axis.

## [0.1.2] - 2026-06-03

### Added
- PyPI long description: `README.md` rewritten for the project page — `pip install pyrrhotite` install instructions, quick-start example, full CLI flag reference, and example output

## [0.1.1] - 2026-06-03

### Added
- `src/point_groups/character_table_generator.py` — automatic character table generator for all seven axial point group families (Cn, Cnh, Cnv, Sn, Dn, Dnh, Dnd) for arbitrary order n ≥ 2, implementing the analytical formulas from Johansson & Veryazov (2017). Exposes `generate_point_group(label)` and `get_or_generate_point_group(label)`. (Moved to `src/character_tables/generator.py` in 0.2.0.)
- `Symmetry._generate_point_group_from_ops` fallback in `_find_point_group`: when no hardcoded group matches the detected operations (e.g. n > 10), the family and order are inferred and the table is generated on-the-fly.
- `tests/test_character_table_generator.py` — 120 tests: consistency against all hardcoded axial tables, off-diagonal row orthogonality for n > 10, structural sanity checks, and spot-checks of known analytical values.

### Fixed
- `testversion.py` was reading `pyrrhotite/_version.py` instead of `src/_version.py`, causing the CI version-check job to fail (`FileNotFoundError`)
- `testversion.py` was also attempting to open `meta.yaml`, which does not exist in the repository; the `meta.yaml` check has been removed

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
