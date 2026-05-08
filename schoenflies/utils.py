"""
utils.py — Shared geometric primitives used across all stages of the algorithm.

Mirrors the role played by the inline geometry helpers scattered throughout
symmetry.cpp and operations/*.cpp in the C++ reference.

Contents (to be implemented):
    GEOMETRY_TOLERANCE  : float  — distance threshold for atom equivalence (0.02 Å)
    INERTIA_TOLERANCE   : float  — threshold for comparing principal moments

    rotation_matrix(axis, order) -> np.ndarray
        Rodrigues' formula: proper rotation matrix for Cn about `axis`.

    reflection_matrix(normal) -> np.ndarray
        Householder reflection matrix for a mirror plane with the given normal.

    improper_rotation_matrix(axis, order) -> np.ndarray
        Sn matrix = Cn rotation composed with reflection through the perpendicular plane.

    apply_operation(matrix, coordinates) -> np.ndarray
        Apply a 3×3 transformation matrix to an (N, 3) coordinate array.

    are_equivalent(transformed, original, elements) -> bool
        Core equivalence check: every transformed atom must coincide with an
        original atom of the same element within GEOMETRY_TOLERANCE.

    normalise(v) -> np.ndarray
        Return a unit vector; raises ValueError for zero-length input.

    are_parallel(a, b) -> bool
        True if a and b point in the same or opposite direction (within tolerance).

    best_fit_plane_normal(points) -> np.ndarray
        SVD-based normal to the plane that best fits a set of 3-D points.
"""
