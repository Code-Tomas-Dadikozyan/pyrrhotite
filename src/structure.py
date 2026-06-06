"""
Molecular structure representation: XYZ loading, centre-of-mass centering,
closest-atom lookup, and bond-pair detection.
Direct translation of reference/src/structure.h/cpp.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .periodic_table import atomic_number, element, get_atomic_number, get_element


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
        """Parse a standard XYZ file (atom count / comment / element x y z lines).

        The XYZ format is:
            Line 0: integer — number of atoms
            Line 1: free-text comment (stored as description)
            Lines 2…N+1: <symbol>  <x>  <y>  <z>  (coordinates in Ångströms)
        """
        with open(path, "r") as fh:
            lines = fh.read().splitlines()

        # Line 0 is the atom count; line 1 is a free-form comment.
        self.num_atoms = int(lines[0].strip())
        self.description = lines[1].strip()

        coords: list[list[float]] = []
        atomic_numbers: list[int] = []

        for i in range(2, 2 + self.num_atoms):
            parts = lines[i].split()
            if len(parts) != 4:
                raise RuntimeError(f"Invalid XYZ line in {path!r}: {lines[i]!r}")
            symbol, x, y, z = parts[0], float(parts[1]), float(parts[2]), float(parts[3])
            # Convert text symbol ("C", "Fe", …) to integer for fast array operations.
            atomic_numbers.append(get_atomic_number(symbol))
            coords.append([x, y, z])

        # Store as NumPy arrays so that vectorised operations (matrix multiply,
        # broadcasting) work efficiently throughout the symmetry search.
        self.atomic_numbers = np.array(atomic_numbers, dtype=int)
        self.coordinates = np.array(coords, dtype=float)

    # ------------------------------------------------------------------
    # Centre of mass
    # ------------------------------------------------------------------

    def _centre_at_com(self) -> None:
        """Translate all coordinates so the centre of mass is at the origin.

        Why this is required
        --------------------
        The symmetry operations (rotations, reflections, inversion) are all
        defined relative to a fixed point.  For a molecule, that fixed point
        must be its centre of mass — the unique point that is left invariant
        by any true molecular symmetry.  If the molecule were off-centre, a
        rotation that is a genuine symmetry would appear to move the molecule
        as a whole, and the algorithm would wrongly reject it.

        The centre of mass is the mass-weighted average position:
            COM = Σ(mᵢ * rᵢ) / Σ(mᵢ)
        Subtracting COM from every coordinate places it at the origin.
        """
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

        This is used during the symmetry search to map a transformed atom
        position back onto a real atom: after applying a candidate symmetry
        operation, each atom should land on top of an atom of the same element.
        If the closest match of the right element is too far away, the operation
        is rejected.

        np.einsum("ij,ij->i", ...) computes the row-wise dot product of a
        matrix with itself, giving squared distances for all candidate atoms
        simultaneously without an explicit Python loop.
        """
        mask = self.atomic_numbers == atomic_number
        indices = np.where(mask)[0]
        diffs = self.coordinates[indices] - coords
        sq_dists = np.einsum("ij,ij->i", diffs, diffs)
        return int(indices[np.argmin(sq_dists)])

    def calculate_bond_pairs(self) -> list[tuple[int, int]]:
        """Return (i, j) index pairs for atoms likely bonded to each other.

        Bond criterion: dist² < 20 · rᵢ · rⱼ   (covalent radii in Ångströms)

        Why this heuristic?
        -------------------
        A typical covalent bond length is approximately rᵢ + rⱼ, so the
        squared bond length is roughly (rᵢ + rⱼ)² ≈ 4 · rᵢ · rⱼ (by the
        AM-GM inequality when rᵢ ≈ rⱼ).  Multiplying by 20 gives a generous
        cutoff — about 2.2 × the expected bond length — that catches stretched
        or unusual bonds without false-positives from non-bonded neighbours.

        Bond pairs are used by the symmetry search to generate candidate C2
        axes (the midpoint bisector of a bond is often a symmetry axis), and
        to build candidate σ planes.
        """
        pairs: list[tuple[int, int]] = []
        for i in range(self.num_atoms - 1):
            ri = get_element(int(self.atomic_numbers[i])).radius
            for j in range(i + 1, self.num_atoms):
                diff = self.coordinates[i] - self.coordinates[j]
                dist2 = float(np.dot(diff, diff))
                rj = get_element(int(self.atomic_numbers[j])).radius
                # Compare squared distance to avoid a square-root per pair.
                if dist2 < 20.0 * ri * rj:
                    pairs.append((i, j))
        return pairs

    @property
    def description_filename(self) -> str:
        """Return a human-readable label combining description and filename."""
        if self.description:
            return f"{self.description} – {self.filename}"
        return self.filename

    def print_atom_list(self) -> None:
        """Print a numbered atom index table: index, element symbol, and coordinates.

        Use this alongside get_atoms_on_axis() / get_atoms_in_plane() results
        to identify which atoms correspond to returned indices.
        """
        print(f"{'#':>4}  {'El':>2}  {'x (Å)':>10}  {'y (Å)':>10}  {'z (Å)':>10}")
        print("─" * 46)
        for i in range(self.num_atoms):
            sym = get_element(int(self.atomic_numbers[i])).symbol
            x, y, z = self.coordinates[i]
            print(f"{i:>4}  {sym:>2}  {x:>10.4f}  {y:>10.4f}  {z:>10.4f}")
