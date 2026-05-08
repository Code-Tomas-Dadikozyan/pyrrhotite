"""
point_group.py — Point group library, scoring, and axis/label assignment.

Corresponds to symmetry/point_groups/ in the C++ reference, which stores
all group definitions and handles the matching and labelling steps that
follow element detection.

Contents (to be implemented):
    @dataclass PGRecord
        symbol      : str
        min_cn      : int              — highest proper axis required
        req_*       : int              — required counts for each element type
        Used by the scoring function to qualify/disqualify candidate groups.

    POINT_GROUP_LIBRARY : list[PGRecord]
        43 entries covering all supported Schoenflies families.
        Order matters: more specific groups should appear before general ones
        so that tie-breaking in _find_best_match favours the correct label.

    class PointGroupClassifier
        Attributes
        ----------
        proper_axes       : list[RotationAxis]
        reflection_planes : list[ReflectionPlane]
        improper_axes     : list[ImproperAxis]
        has_inversion     : bool
        rotor_type        : RotorType
        point_group       : str        — final Schoenflies symbol, e.g. "D6h"
        z_axis            : np.ndarray — principal (highest-Cn) axis
        x_axis            : np.ndarray — chosen to maximise atoms in xz plane

        Methods
        -------
        __init__(finder: SymmetryFinder) -> None

        classify() -> str
            Full pipeline: handle linear special case, score library, pick
            best match, assign Cartesian axes, label operations, return symbol.

        _score(record: PGRecord) -> float
            Return 0 for exact match, positive for surplus elements,
            -1 (disqualified) if required elements are absent.

        _find_best_match() -> PGRecord
            Return the qualified record with the lowest score.

        _find_cartesian_axes() -> None
            Set z_axis to the highest-order Cn direction;
            call _choose_x_axis to set x_axis.

        _choose_x_axis() -> np.ndarray
            Project atoms into the plane perpendicular to z, count atoms
            near each candidate direction, pick the direction with the most.

        _label_operations() -> None
            Assign σh / σv / σd labels to ReflectionPlane objects and
            C2′ / C2′′ labels to secondary C2 RotationAxis objects based
            on their angle to z_axis and to σv planes.
"""
