# Changelog

All notable changes to this project will be documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [0.1.0] - 2026-05-11

### Added
- Full Python translation of the Schoenflies point group determination algorithm from the C++ reference implementation (`reference/src/`)
- `schoenflies/periodic_table.py` — hardcoded atomic data (symbol, mass, covalent radius, colour) for all 118 elements, translated from `reference/src/periodic_table/periodic_table.cpp`
- `schoenflies/rotor_class.py` — `RotorClass` enum (AsymmetricTop, OblateSymmetricTop, ProlateSymmetricTop, Linear, SphericalTop)
- `schoenflies/structure.py` — `Structure` class: XYZ file loading, centre-of-mass centering, closest-atom lookup, bond-pair detection
- `schoenflies/operations/operation_label.py` — `OperationLabel` with inner `Element`, `Plane`, and `Prime` enums; factory classmethods mirroring C++ overloaded constructors
- `schoenflies/operations/operation_label_count.py` — `OperationLabelCount` pairing a label with a multiplicity count
- `schoenflies/operations/operation_group.py` — `OperationGroup` grouping operation IDs under a shared label
- `schoenflies/operations/operation.py` — `Operation` class: Rodrigues rotation matrices, Householder reflection matrices, inversion, improper rotation; `do_operation` atom-mapping with normalised error metric
- `schoenflies/operations/operation_manager.py` — `OperationManager`: validates, deduplicates, and stores found operations; generates the final labelled point-group operation set
- `schoenflies/point_groups/irrep_label.py` — `IrrepLabel` with `Mulliken`, `Parity`, and `Prime` enums for Mulliken notation
- `schoenflies/point_groups/point_group_label.py` — `PointGroupLabel` with `Class` enum covering all 18 point-group families including C∞v and D∞h
- `schoenflies/point_groups/point_group.py` — `PointGroup` class with `compare_to_symmetry_operations` used by the matching algorithm
- `schoenflies/point_groups/point_groups.py` — hardcoded definitions for all 54+ point groups with operation counts, irreducible representations, and character tables
- `schoenflies/symmetry.py` — `Symmetry` class: full 7-step pipeline (principal axes via inertia tensor, rotor classification, symmetry-operation search, point-group matching, Cartesian axis assignment, operation labelling, point-group operation generation)
- `tests/files/` — 32 XYZ test molecules copied from `reference/test/files/` covering all major point-group families
- `tests/conftest.py` — pytest fixtures and expected point-group label mapping for all 32 molecules
- `tests/test_structure.py` — unit tests for XYZ loading, COM centering, `find_closest_index`, and `calculate_bond_pairs`