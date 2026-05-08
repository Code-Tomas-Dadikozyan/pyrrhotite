"""
molecule.py — Molecule loading, inertia tensor construction, and rotor classification.

Corresponds to structure.h / structure.cpp in the C++ reference, which handles
XYZ file I/O, centre-of-mass translation, and the physical data (coordinates,
atomic numbers) that the symmetry stage consumes.

The rotor classification step (absent from structure.cpp but present in
symmetry.cpp) is included here because it depends only on the inertia tensor
and logically belongs with the molecule data.

Contents (to be implemented):
    ATOMIC_MASSES : dict[str, float]
        Atomic mass table for centre-of-mass calculation (common elements).

    class RotorType(enum.Enum)
        LINEAR, SPHERICAL_TOP, PROLATE_SYMMETRIC, OBLATE_SYMMETRIC, ASYMMETRIC

    class Molecule
        Attributes
        ----------
        symbols      : list[str]       — element symbols, length N
        coordinates  : np.ndarray      — shape (N, 3), Ångströms, COM-centred
        atomic_numbers : np.ndarray    — shape (N,), integer
        principal_moments : np.ndarray — shape (3,), ascending eigenvalues (amu·Å²)
        principal_axes   : np.ndarray  — shape (3, 3), columns = eigenvectors
        rotor_type       : RotorType

        Methods
        -------
        __init__(path: str) -> None
            Load XYZ, centre at COM, build and diagonalise inertia tensor,
            classify rotor.

        _load_xyz(path: str) -> None
            Parse the two-line header and per-atom coordinate lines.

        _centre_on_com() -> None
            Translate coordinates so the centre of mass is at the origin.

        _compute_inertia_tensor() -> np.ndarray
            Build the 3×3 inertia tensor from current coordinates.

        _diagonalise(tensor: np.ndarray) -> None
            Eigendecompose via numpy.linalg.eigh; store moments and axes.

        _classify_rotor() -> RotorType
            Compare principal moments within INERTIA_TOLERANCE to assign type.
"""
