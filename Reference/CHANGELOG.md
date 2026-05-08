# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Unreleased

## [1.1.1] - 2022-06-06
### Fixed
- The _σ_<sub>v</sub>&#x2032; symmetry operation is now correctly visible for
  the _D_<sub>2h</sub> point group (see issue #2)
- The program no longer crashes when practice is started without any modules
  selected (see issue #3)
- The flowchart practice module now shows the correct answer to the question
  whether a molecule has two or more _C<sub>n</sub>_ (_n_ > 2) for point groups
  with many higher-order rotations (see issue #4)

## [1.1.0] - 2022-05-10
### Added
- Built-in library of 36 example structures (File → Open from library)
- Character table viewer (View → Character tables)
- Support for labeling atoms on the structure (View → Show atom labels)
- Three types of randomly generated practice exercises using the library
  - Determining the point group of a structure
  - Determining the irreducible representations to which a basis set belongs
  - Applying the projection operator to an orbital of a single atom

### Fixed
- Explicitly add a return code when running Schoenflies from the command line
  (see issue #1)

## [1.0.0] - 2022-02-04
### Added
- Initial release

[Unreleased]: https://gitlab.com/lkkmpn/schoenflies/-/compare/1.1.1...main
[1.1.1]: https://gitlab.com/lkkmpn/schoenflies/-/compare/1.1.0...1.1.1
[1.1.0]: https://gitlab.com/lkkmpn/schoenflies/-/compare/1.0.0...1.1.0
[1.0.0]: https://gitlab.com/lkkmpn/schoenflies/-/releases/1.0.0
