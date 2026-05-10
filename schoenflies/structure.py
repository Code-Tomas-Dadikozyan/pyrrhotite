"""
Molecular structure representation: XYZ loading, centre-of-mass centering,
closest-atom lookup, and bond-pair detection.
Direct translation of reference/src/structure.h/cpp.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .periodic_table import get_atomic_number, get_element


class Structure:
    """Holds atom coordinates and atomic numbers for a single molecule."""

    def __init__(self, path: str | None = None) -> None:
        """Load a structure from an XYZ file and centre it at its centre of mass.

        If path is None an empty structure is created (useful for testing).
        """
        self.num_atoms: int = 0
        self.coordinates: np.ndarray = np.empty((0, 3), dtype=float)
        self.atomic_numbers: np.ndarray = np.empty(0, dtype=int)
        self.description: str = ""
        self.filename: str = ""

        if path is not None:
            self._load_from_file(path)
            self._centre_at_com()

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load_from_file(self, path: str) -> None:
        """Dispatch to the appropriate loader based on file extension."""
        p = Path(path)
        self.filename = p.name
        if self.filename.endswith(".xyz"):
            self._load_from_xyz(path)
        else:
            raise RuntimeError(f"File format not supported: {path}")

    def _load_from_xyz(self, path: str) -> None:
        """Parse a standard XYZ file (atom count / comment / element x y z lines)."""
        with open(path, "r") as fh:
            lines = fh.read().splitlines()

        self.num_atoms = int(lines[0].strip())
        self.description = lines[1].strip()

        coords: list[list[float]] = []
        atomic_numbers: list[int] = []

        for i in range(2, 2 + self.num_atoms):
            parts = lines[i].split()
            if len(parts) != 4:
                raise RuntimeError(f"Invalid XYZ line in {path!r}: {lines[i]!r}")
            symbol, x, y, z = parts[0], float(parts[1]), float(parts[2]), float(parts[3])
            atomic_numbers.append(get_atomic_number(symbol))
            coords.append([x, y, z])

        self.atomic_numbers = np.array(atomic_numbers, dtype=int)
        self.coordinates = np.array(coords, dtype=float)

    # ------------------------------------------------------------------
    # Centre of mass
    # ------------------------------------------------------------------

    def _centre_at_com(self) -> None:
        """Translate all coordinates so the centre of mass is at the origin."""
        masses = np.array([get_element(int(z)).mass for z in self.atomic_numbers])
        com = np.average(self.coordinates, axis=0, weights=masses)
        self.coordinates -= com

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def find_closest_index(self, coords: np.ndarray, atomic_number: int) -> int:
        """Return the index of the atom of the given element closest to coords.

        Only atoms whose atomic number matches are considered, mirroring
        reference/src/structure.cpp find_closest_index.
        """
        mask = self.atomic_numbers == atomic_number
        indices = np.where(mask)[0]
        diffs = self.coordinates[indices] - coords
        sq_dists = np.einsum("ij,ij->i", diffs, diffs)
        return int(indices[np.argmin(sq_dists)])

    def calculate_bond_pairs(self) -> list[tuple[int, int]]:
        """Return (i, j) index pairs for atoms likely bonded to each other.

        Criterion: dist² < 20 * r_i * r_j  (covalent radii in Angstrom).
        """
        pairs: list[tuple[int, int]] = []
        for i in range(self.num_atoms - 1):
            ri = get_element(int(self.atomic_numbers[i])).radius
            for j in range(i + 1, self.num_atoms):
                diff = self.coordinates[i] - self.coordinates[j]
                dist2 = float(np.dot(diff, diff))
                rj = get_element(int(self.atomic_numbers[j])).radius
                if dist2 < 20.0 * ri * rj:
                    pairs.append((i, j))
        return pairs

    def get_description_filename(self) -> str:
        """Return a human-readable label combining description and filename."""
        if self.description:
            return f"{self.description} – {self.filename}"
        return self.filename
