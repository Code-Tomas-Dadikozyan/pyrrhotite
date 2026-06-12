# API Reference

This page is generated directly from the docstrings in the source, so it always
matches the installed version. For task-oriented walkthroughs with runnable
examples, see the [User Guide](user-guide.md); this page is the exhaustive
signature-level reference.

!!! note "Scope"
    Only the public, supported API is documented here. The 3-D visualizer's
    internal modules (which require the optional `vis` extras) are intentionally
    omitted — use the [`visualize` helpers](#visualization) below instead.

---

## Core

::: pyrrhotite.Structure

::: pyrrhotite.Symmetry

::: pyrrhotite.RotorClass

---

## Structure generation

::: pyrrhotite.generate_idealized_structure

::: pyrrhotite.write_xyz

::: pyrrhotite.structure_generator.format_xyz

---

## Character tables

::: pyrrhotite.character_tables.get_or_generate_point_group

::: pyrrhotite.character_tables.generate_point_group

::: pyrrhotite.character_tables.find_point_group

::: pyrrhotite.character_tables.parse_point_group_name

::: pyrrhotite.character_tables.print_character_table_for

::: pyrrhotite.character_tables.format_html

::: pyrrhotite.character_tables.save_html

::: pyrrhotite.character_tables.format_latex

::: pyrrhotite.character_tables.save_latex

---

## Point groups & basis functions

::: pyrrhotite.point_groups.point_group.PointGroup

::: pyrrhotite.point_groups.basis_functions.compute_basis_functions

---

## Element data

::: pyrrhotite.periodic_table.get_element

::: pyrrhotite.periodic_table.get_atomic_number

::: pyrrhotite.periodic_table.Element

---

## Sample molecules

::: pyrrhotite.list_sample_molecules

::: pyrrhotite.load_sample

::: pyrrhotite.analyse_sample

::: pyrrhotite.show_character_table_sample

---

## Visualization

!!! warning "Requires the `vis` extras"
    These open an interactive window and need `pip install 'pyrrhotite[vis]'`.
    See [Getting Started → Optional extras](getting-started.md#optional-extras).

::: pyrrhotite.visualize

::: pyrrhotite.visualize_idealized_structure

::: pyrrhotite.visualize_sample
