"""
molecule.py — Molecule class

Loads a .xyz file, computes the inertia tensor, diagonalises it to get
principal axes and moments, and classifies the molecule's rotor type.
This is the first stage of the Schoenflies algorithm: before we can search
for symmetry elements we need to know the molecule's natural Cartesian frame.
"""

import numpy as np
from .utils import INERTIA_TOLERANCE

# ---------------------------------------------------------------------------
# Atomic mass table  (standard atomic weights in atomic mass units, u)
# ---------------------------------------------------------------------------
# Only elements that appear in common test molecules are listed.
# Source: IUPAC 2021 atomic weights (abridged to 4 significant figures).
# If an element is missing the code raises a clear KeyError rather than
# silently using a wrong mass.

ATOMIC_MASSES: dict[str, float] = {
    'H':   1.008,
    'He':  4.003,
    'Li':  6.941,
    'Be':  9.012,
    'B':  10.81,
    'C':  12.01,
    'N':  14.01,
    'O':  16.00,
    'F':  19.00,
    'Ne': 20.18,
    'Na': 22.99,
    'Mg': 24.31,
    'Al': 26.98,
    'Si': 28.09,
    'P':  30.97,
    'S':  32.06,
    'Cl': 35.45,
    'Ar': 39.95,
    'K':  39.10,
    'Ca': 40.08,
    'Fe': 55.85,
    'Br': 79.90,
    'I': 126.90,
}

# Rotor type labels — these mirror the four cases in the C++ source.
ROTOR_LINEAR            = 'linear'
ROTOR_SPHERICAL_TOP     = 'spherical_top'
ROTOR_PROLATE_SYMMETRIC = 'prolate_symmetric_top'   # Ia < Ib ≈ Ic  (elongated, like a rugby ball)
ROTOR_OBLATE_SYMMETRIC  = 'oblate_symmetric_top'    # Ia ≈ Ib < Ic  (flattened, like a discus)
ROTOR_ASYMMETRIC        = 'asymmetric_top'


# ---------------------------------------------------------------------------
# Molecule class
# ---------------------------------------------------------------------------

class Molecule:
    """
    Represents a molecule loaded from a .xyz file.

    After construction the molecule is centred on its centre of mass.
    The inertia tensor is computed and diagonalised, giving:
      - self.principal_moments  : the three eigenvalues Ia ≤ Ib ≤ Ic (amu·Å²)
      - self.principal_axes     : the corresponding eigenvectors as columns
      - self.rotor_type         : one of the five ROTOR_* string constants

    Attributes
    ----------
    elements        : list[str]       element symbol for each atom
    coords          : np.ndarray (N,3) Cartesian coordinates in Å, COM-centred
    masses          : np.ndarray (N,)  atomic mass of each atom in amu
    inertia_tensor  : np.ndarray (3,3) symmetric inertia tensor in amu·Å²
    principal_moments: np.ndarray (3,) eigenvalues, ascending (Ia ≤ Ib ≤ Ic)
    principal_axes  : np.ndarray (3,3) columns are eigenvectors of the tensor
    rotor_type      : str             one of the ROTOR_* constants above
    """

    def __init__(self, filepath: str) -> None:
        self.elements, self.coords = self._load_xyz(filepath)
        self.masses = np.array([ATOMIC_MASSES[e] for e in self.elements])

        self._centre_on_com()
        self.inertia_tensor = self._compute_inertia_tensor()
        self.principal_moments, self.principal_axes = self._diagonalise()
        self.rotor_type = self._classify_rotor()

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load_xyz(self, filepath: str) -> tuple[list[str], np.ndarray]:
        """
        Parse a .xyz file and return (elements, coords).

        .xyz format
        -----------
        Line 1 : integer — number of atoms
        Line 2 : comment (ignored)
        Lines 3+: element_symbol  x  y  z   (coordinates in Angstroms)

        Parameters
        ----------
        filepath : path to the .xyz file

        Returns
        -------
        elements : list of N element symbol strings
        coords   : np.ndarray shape (N, 3), float64, units = Å
        """
        with open(filepath) as f:
            lines = f.readlines()

        n_atoms = int(lines[0].strip())
        # line 1 (index 1) is the comment — skip it
        elements = []
        coords   = []
        for line in lines[2: 2 + n_atoms]:
            parts = line.split()
            elements.append(parts[0])
            coords.append([float(parts[1]), float(parts[2]), float(parts[3])])

        return elements, np.array(coords, dtype=float)

    # ------------------------------------------------------------------
    # Centre of mass
    # ------------------------------------------------------------------

    def _centre_on_com(self) -> None:
        """
        Translate all coordinates so the centre of mass is at the origin.

        Chemistry meaning
        -----------------
        Symmetry operations (rotations, reflections) only make sense when
        performed around/through the molecule's centre.  By shifting the COM
        to the origin first, every candidate rotation axis passes through
        the origin and every mirror plane passes through the origin, which
        enormously simplifies the geometry checks later.

        The centre of mass is the mass-weighted average position:
            r_COM = Σ(m_i · r_i) / Σ(m_i)
        """
        com = np.sum(self.masses[:, np.newaxis] * self.coords, axis=0) / self.masses.sum()
        self.coords -= com

    # ------------------------------------------------------------------
    # Inertia tensor
    # ------------------------------------------------------------------

    def _compute_inertia_tensor(self) -> np.ndarray:
        """
        Compute the 3x3 inertia tensor of the molecule.

        Chemistry meaning
        -----------------
        The inertia tensor describes how mass is distributed in 3D space.
        Diagonalising it gives the three PRINCIPAL MOMENTS OF INERTIA
        (Ia ≤ Ib ≤ Ic) and the PRINCIPAL AXES — the natural Cartesian
        frame of the molecule.  The symmetry of the principal moments tells
        us what kind of rotor the molecule is, which guides the whole
        symmetry search.

        For example:
        - All three moments equal → spherical top → must look for Td, Oh, Ih
        - Two moments equal, one smaller → prolate symmetric top → C3v, D3h …
        - Two moments equal, one larger → oblate symmetric top → D6h, D3h …
        - All different → asymmetric top → C2v, D2h, C1 …
        - One moment ≈ 0 → linear molecule → C∞v or D∞h

        Tensor elements (with COM at origin, so Σ m_i r_i = 0)
        -------------------------------------------------------
          I_xx = Σ m_i (y_i² + z_i²)
          I_yy = Σ m_i (x_i² + z_i²)
          I_zz = Σ m_i (x_i² + y_i²)
          I_xy = I_yx = −Σ m_i x_i y_i
          I_xz = I_zx = −Σ m_i x_i z_i
          I_yz = I_zy = −Σ m_i y_i z_i

        Returns
        -------
        I : np.ndarray shape (3, 3), symmetric, units = amu·Å²
        """
        x, y, z = self.coords[:, 0], self.coords[:, 1], self.coords[:, 2]
        m = self.masses

        Ixx = np.sum(m * (y**2 + z**2))
        Iyy = np.sum(m * (x**2 + z**2))
        Izz = np.sum(m * (x**2 + y**2))
        Ixy = -np.sum(m * x * y)
        Ixz = -np.sum(m * x * z)
        Iyz = -np.sum(m * y * z)

        return np.array([
            [Ixx, Ixy, Ixz],
            [Ixy, Iyy, Iyz],
            [Ixz, Iyz, Izz],
        ])

    # ------------------------------------------------------------------
    # Diagonalisation
    # ------------------------------------------------------------------

    def _diagonalise(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Diagonalise the inertia tensor to get principal moments and axes.

        numpy.linalg.eigh is used because the inertia tensor is real and
        symmetric (the 'h' stands for Hermitian — symmetric is the real
        special case).  It returns eigenvalues in ASCENDING order, which
        matches the convention Ia ≤ Ib ≤ Ic used in the C++ source
        (Eigen's SelfAdjointEigenSolver also sorts ascending).

        Python/C++ divergence note
        --------------------------
        numpy stores arrays in row-major (C) order; Eigen uses column-major
        (Fortran) order.  For a symmetric matrix this makes no difference:
        eigenvectors come out the same.  However, numpy.linalg.eigh returns
        eigenvectors as COLUMNS of the output matrix `vecs`, i.e. vecs[:,i]
        is the eigenvector for eigenvalues[i].  This is the same convention
        as Eigen's `.eigenvectors()` method.

        Returns
        -------
        moments : np.ndarray (3,)   principal moments Ia ≤ Ib ≤ Ic
        axes    : np.ndarray (3,3)  axes[:,i] is the principal axis for moments[i]
        """
        moments, axes = np.linalg.eigh(self.inertia_tensor)
        # eigh already returns ascending eigenvalues — no re-sorting needed.
        return moments, axes

    # ------------------------------------------------------------------
    # Rotor classification
    # ------------------------------------------------------------------

    def _classify_rotor(self) -> str:
        """
        Classify the molecule as one of five rotor types based on the
        degeneracy of its principal moments of inertia.

        Chemistry meaning
        -----------------
        Every molecule can be assigned to one of these classes, which
        determines what symmetry elements are even worth searching for:

        Linear (Ia ≈ 0):
            All atoms lie on a single line.  The only possible groups are
            C∞v and D∞h.  We detect this by checking whether the smallest
            moment is essentially zero (all mass lies on one axis → no
            rotational inertia about that axis).

        Spherical top (Ia ≈ Ib ≈ Ic):
            Mass is distributed equally in all three directions, like a
            perfect sphere.  Only Td, Oh, and Ih are possible.  Examples:
            CH4, SF6, C60.

        Prolate symmetric top (Ia < Ib ≈ Ic):
            The molecule is elongated like a rugby ball — it spins easily
            about its long axis but is harder to spin end-over-end.
            Examples: NH3 (C3v), ferrocene (D5h).

        Oblate symmetric top (Ia ≈ Ib < Ic):
            The molecule is flattened like a discus — easiest to spin
            about the axis perpendicular to the flat face.
            Examples: benzene (D6h), BF3 (D3h).

        Asymmetric top (all different):
            All three moments are distinct.  Most molecules with lower
            symmetry fall here.  Examples: H2O (C2v), H2O2 (C2).

        Tolerance
        ---------
        Two moments are considered equal if |Ia - Ib| / max(Ib, 1e-10) < tol.
        Using a relative tolerance handles the fact that moments scale with
        molecular size.  A small absolute floor (1e-10) avoids division by
        zero for the near-zero linear case.

        Returns
        -------
        str : one of the ROTOR_* module-level constants
        """
        Ia, Ib, Ic = self.principal_moments
        tol = INERTIA_TOLERANCE

        def near(a: float, b: float) -> bool:
            denom = max(abs(b), 1e-10)
            return abs(a - b) / denom < tol

        if near(Ia, 0.0):
            return ROTOR_LINEAR

        if near(Ia, Ib) and near(Ib, Ic):
            return ROTOR_SPHERICAL_TOP

        if near(Ib, Ic):
            return ROTOR_PROLATE_SYMMETRIC

        if near(Ia, Ib):
            return ROTOR_OBLATE_SYMMETRIC

        return ROTOR_ASYMMETRIC

    # ------------------------------------------------------------------
    # String representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Molecule(n_atoms={len(self.elements)}, "
            f"rotor='{self.rotor_type}', "
            f"moments=[{self.principal_moments[0]:.3f}, "
            f"{self.principal_moments[1]:.3f}, "
            f"{self.principal_moments[2]:.3f}] amu·Å²)"
        )
