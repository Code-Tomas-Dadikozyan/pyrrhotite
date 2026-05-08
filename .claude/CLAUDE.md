# CLAUDE.md — Schoenflies Point Group Determination

## Project Goal
Translate and implement the Schoenflies point group determination algorithm in Python.
The reference C++ implementation is in `reference/`. The goal is a functionally
equivalent Python package in `schoenflies/` that follows the structure of the original
as closely as possible.

## Repository Structure
```
schoenflies_python/
│
├── .claude/
│   ├── .claudeignore       ← Claude config. Do not modify.
│   └── CLAUDE.md           ← This file.
│
├── .vscode/                ← Editor settings. Ignore.
├── reference/              ← READ ONLY. Original C++ source. Never modify.
├── schoenflies/      ← Primary working directory. All new code goes here.
├── tests/            ← Test files. You may create and run these.
├── version1/               ← READ ONLY. Archived earlier attempt. Never modify.
│
├── .gitignore              ← Do not modify.
├── CHANGELOG.md            ← Update when meaningful changes are made.
├── LICENSE                 ← Do not modify.
├── pyproject.toml          ← Do not modify unless explicitly instructed.
└── README.md               ← Do not modify unless explicitly instructed.
```

## Permissions

### You MAY
- Read any file in the repository
- Create and edit files inside `schoenflies/` and `tests/`
- Run `pytest` and `python`
- Install packages explicitly listed under dependencies in `pyproject.toml`

### You MAY NOT
- Modify anything inside `reference/` or `version1/`
- Modify `pyproject.toml`, `.gitignore`, or `.claudeignore` unless explicitly asked
- Install packages not listed in `pyproject.toml` without asking first
- Refactor working, tested code unless explicitly instructed

## Coding Conventions
- Python 3.10+
- Type hints required on all function signatures
- NumPy arrays preferred over plain lists for numerical data
- Each function must have a docstring explaining its role in the algorithm
- Follow the structure and logic of the C++ reference as closely as Python allows
- Comment any location where a C++ idiom required a non-obvious Python equivalent