"""
Hardcoded character tables for all standard Schoenflies point groups.

Why hardcoded rather than generated?
-------------------------------------
For low-order groups (roughly n ≤ 10), hardcoding the character tables is
more reliable than generating them analytically:
- Polyhedral groups (T, Td, Th, O, Oh, I, Ih) and special groups (Cs, Ci,
  C1) have irregular structures that do not fit the axial generator formulas.
- For high-order axial groups not listed here, the character_table_generator
  module produces tables analytically on demand.

How to read this file
---------------------
Each entry is a PointGroup() constructor call.  The positional arguments are:
  1. label          — PointGroupLabel(class, order), e.g. Label(Class.C2v, 2)
  2. order          — total number of symmetry operations in the group
  3. num_inversions — 0 or 1 (1 if the group has an inversion centre)
  4. num_proper_rotations   — dict {degree: count}, e.g. {2: 1} for one C2
  5. num_improper_rotations — dict {degree: count}
  6. num_reflections        — integer count of σ planes
  7. unique_operations      — list[OperationLabelCount] giving the character
                              table column headers (E is implicit / not listed)
  8. irreps          — list[IrrepLabel] giving the row labels
  9. characters      — list[list[float]], outer index = irrep, inner = column
                       (first inner element is always χ(E) = dimension)

Trigonometric constants
-----------------------
The constants TCaP b = 2 cos(a·π / b) appear as irrational character values
in groups with 5-, 7-, 8-, 9-, and 10-fold axes.  Storing them as named
constants (rather than inline floats) keeps the character table entries
exact and readable.  For example, TC1P5 ≈ 1.6180 is the golden ratio φ,
which appears in the character tables of icosahedral groups.
"""

from __future__ import annotations

import math

from ..operations.operation_label import OperationLabel
Element = OperationLabel.Element
Plane   = OperationLabel.Plane
OPrime  = OperationLabel.Prime
from ..operations.operation_label_count import OperationLabelCount
from .irrep_label import IrrepLabel
Mulliken   = IrrepLabel.Mulliken
IrrepParity = IrrepLabel.Parity
IrrepPrime  = IrrepLabel.Prime
from .point_group_label import PointGroupLabel
PGClass = PointGroupLabel.Class
from .point_group import PointGroup

# ---------------------------------------------------------------------------
# Trigonometric constants  (C++ header: point_groups.h)
# Naming: TC<a>P<b>  =  2 * cos(a * π / b)
# These values appear as exact character values for axes of order 5, 7, 8, 9, 10.
# ---------------------------------------------------------------------------
TC1P4  = 2.0 * math.cos(1.0 * math.pi / 4.0)   # ≈  1.4142  (√2)
TC1P5  = 2.0 * math.cos(1.0 * math.pi / 5.0)   # ≈  1.6180  (golden ratio φ)
TC2P5  = 2.0 * math.cos(2.0 * math.pi / 5.0)   # ≈  0.6180  (φ − 1)
TC1P6  = 2.0 * math.cos(1.0 * math.pi / 6.0)   # ≈  1.7321  (√3)
TC1P7  = 2.0 * math.cos(1.0 * math.pi / 7.0)   # ≈  1.8019
TC2P7  = 2.0 * math.cos(2.0 * math.pi / 7.0)   # ≈  1.2470
TC3P7  = 2.0 * math.cos(3.0 * math.pi / 7.0)   # ≈  0.4450
TC1P8  = 2.0 * math.cos(1.0 * math.pi / 8.0)   # ≈  1.8478
TC3P8  = 2.0 * math.cos(3.0 * math.pi / 8.0)   # ≈  0.7654
TC1P9  = 2.0 * math.cos(1.0 * math.pi / 9.0)   # ≈  1.8794
TC2P9  = 2.0 * math.cos(2.0 * math.pi / 9.0)   # ≈  1.5321
TC4P9  = 2.0 * math.cos(4.0 * math.pi / 9.0)   # ≈  0.3473
TC1P10 = 2.0 * math.cos(1.0 * math.pi / 10.0)  # ≈  1.9021
TC3P10 = 2.0 * math.cos(3.0 * math.pi / 10.0)  # ≈  1.1756

# Sentinel values used where n → ∞  (e.g. C∞v, D∞h).
# The integer 0 is used as a stand-in for infinity in axis degree and count.
DEGREE_INF = 0
COUNT_INF  = 0

# ---------------------------------------------------------------------------
# Short aliases  (mirror the C++ typedefs in point_groups.h)
# These single-letter aliases keep the PointGroup() calls below compact and
# readable.  Compare with the C++ source, which uses identical short names.
# ---------------------------------------------------------------------------
Label   = PointGroupLabel
Class   = PGClass
O       = OperationLabel     # O for Operation-label
E       = Element
OPlane  = Plane
I       = IrrepLabel         # I for Irrep-label
M       = Mulliken
IParity = IrrepParity
IPrime  = IrrepPrime

# ---------------------------------------------------------------------------
# PointGroup constructor positional order:
#   PointGroup(label, order, num_inversions,
#              num_proper_rotations: dict[int, int],
#              num_improper_rotations: dict[int, int],
#              num_reflections: int,
#              unique_operations: list[OperationLabelCount],
#              irreps: list[IrrepLabel],
#              characters: list[list[float]])
#
# unique_operations uses OperationLabelCount(count, OperationLabel(...)).
# The identity E column is always first in the character table but is NOT
# listed in unique_operations — it is implicit (χ(E) = dimension of irrep).
# ---------------------------------------------------------------------------

POINT_GROUPS: list[PointGroup] = [

    # -----------------------------------------------------------------------
    # Nonaxial symmetries  (3 groups)
    # No rotation axes (or only trivial identity); the simplest groups.
    # -----------------------------------------------------------------------

    # C1 ─ trivial group, only the identity
    PointGroup(
        Label(Class.C, 1), 1, 0, {}, {}, 0,
        [],
        [I(M.A)],
        [[1.0]],
    ),

    # Ci ─ inversion group
    PointGroup(
        Label(Class.Ci), 2, 1, {}, {}, 0,
        [OperationLabelCount(1, O(E.I))],
        [I(M.A, IParity.g), I(M.A, IParity.u)],
        [[1.0,  1.0],
         [1.0, -1.0]],
    ),

    # Cs ─ single mirror plane (σh)
    PointGroup(
        Label(Class.Cs), 2, 0, {}, {}, 1,
        [OperationLabelCount(1, O(E.sigma, OPlane.h))],
        [I(M.A, IPrime.Single), I(M.A, IPrime.Double)],
        [[1.0,  1.0],
         [1.0, -1.0]],
    ),

    # -----------------------------------------------------------------------
    # Cyclic groups  Cn  (9 groups: C2 … C10)
    # Only a Cn rotation axis; no mirrors, no inversion.  Always chiral.
    # -----------------------------------------------------------------------

    # C2
    PointGroup(
        Label(Class.C, 2), 2, 0, {2: 1}, {}, 0,
        [OperationLabelCount(1, O(E.C, 2))],
        [I(M.A), I(M.B)],
        [[1.0,  1.0],
         [1.0, -1.0]],
    ),

    # C3
    PointGroup(
        Label(Class.C, 3), 3, 0, {3: 1}, {}, 0,
        [OperationLabelCount(2, O(E.C, 3))],
        [I(M.A), I(M.E)],
        [[1.0,  1.0],
         [2.0, -1.0]],
    ),

    # C4
    PointGroup(
        Label(Class.C, 4), 4, 0, {4: 1, 2: 1}, {}, 0,
        [OperationLabelCount(2, O(E.C, 4)),
         OperationLabelCount(1, O(E.C, 2))],
        [I(M.A), I(M.B), I(M.E)],
        [[1.0,  1.0,  1.0],
         [1.0, -1.0,  1.0],
         [2.0,  0.0, -2.0]],
    ),

    # C5
    PointGroup(
        Label(Class.C, 5), 5, 0, {5: 1}, {}, 0,
        [OperationLabelCount(2, O(E.C, 5)),
         OperationLabelCount(2, O(E.C, 5, 2))],
        [I(M.A), I(M.E, 1), I(M.E, 2)],
        [[1.0,  1.0,      1.0    ],
         [2.0,  TC2P5,   -TC1P5  ],
         [2.0, -TC1P5,    TC2P5  ]],
    ),

    # C6
    PointGroup(
        Label(Class.C, 6), 6, 0, {6: 1, 3: 1, 2: 1}, {}, 0,
        [OperationLabelCount(2, O(E.C, 6)),
         OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(1, O(E.C, 2))],
        [I(M.A), I(M.B), I(M.E, 1), I(M.E, 2)],
        [[1.0,  1.0,  1.0,  1.0],
         [1.0, -1.0,  1.0, -1.0],
         [2.0,  1.0, -1.0, -2.0],
         [2.0, -1.0, -1.0,  2.0]],
    ),

    # C7
    PointGroup(
        Label(Class.C, 7), 7, 0, {7: 1}, {}, 0,
        [OperationLabelCount(2, O(E.C, 7)),
         OperationLabelCount(2, O(E.C, 7, 2)),
         OperationLabelCount(2, O(E.C, 7, 3))],
        [I(M.A), I(M.E, 1), I(M.E, 2), I(M.E, 3)],
        [[1.0,  1.0,      1.0,     1.0    ],
         [2.0,  TC2P7,   -TC3P7,  -TC1P7  ],
         [2.0, -TC3P7,   -TC1P7,   TC2P7  ],
         [2.0, -TC1P7,    TC2P7,  -TC3P7  ]],
    ),

    # C8
    PointGroup(
        Label(Class.C, 8), 8, 0, {8: 1, 4: 1, 2: 1}, {}, 0,
        [OperationLabelCount(2, O(E.C, 8)),
         OperationLabelCount(2, O(E.C, 4)),
         OperationLabelCount(2, O(E.C, 8, 3)),
         OperationLabelCount(1, O(E.C, 2))],
        [I(M.A), I(M.B), I(M.E, 1), I(M.E, 2), I(M.E, 3)],
        [[1.0,  1.0,    1.0,    1.0,    1.0 ],
         [1.0, -1.0,    1.0,   -1.0,    1.0 ],
         [2.0,  TC1P4,  0.0,  -TC1P4,  -2.0 ],
         [2.0,  0.0,   -2.0,   0.0,    2.0  ],
         [2.0, -TC1P4,  0.0,   TC1P4,  -2.0 ]],
    ),

    # C9
    PointGroup(
        Label(Class.C, 9), 9, 0, {9: 1, 3: 1}, {}, 0,
        [OperationLabelCount(2, O(E.C, 9)),
         OperationLabelCount(2, O(E.C, 9, 2)),
         OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(2, O(E.C, 9, 4))],
        [I(M.A), I(M.E, 1), I(M.E, 2), I(M.E, 3), I(M.E, 4)],
        [[1.0,  1.0,     1.0,    1.0,    1.0    ],
         [2.0,  TC2P9,   TC4P9,  -1.0,  -TC1P9  ],
         [2.0,  TC4P9,  -TC1P9,  -1.0,   TC2P9  ],
         [2.0,  -1.0,   -1.0,    2.0,   -1.0    ],
         [2.0, -TC1P9,   TC2P9,  -1.0,   TC4P9  ]],
    ),

    # C10
    PointGroup(
        Label(Class.C, 10), 10, 0, {10: 1, 5: 1, 2: 1}, {}, 0,
        [OperationLabelCount(2, O(E.C, 10)),
         OperationLabelCount(2, O(E.C, 5)),
         OperationLabelCount(2, O(E.C, 10, 3)),
         OperationLabelCount(2, O(E.C, 5, 2)),
         OperationLabelCount(1, O(E.C, 2))],
        [I(M.A), I(M.B), I(M.E, 1), I(M.E, 2), I(M.E, 3), I(M.E, 4)],
        [[1.0,  1.0,     1.0,     1.0,     1.0,     1.0  ],
         [1.0, -1.0,     1.0,    -1.0,     1.0,    -1.0  ],
         [2.0,  TC1P5,   TC2P5,  -TC2P5,  -TC1P5,  -2.0  ],
         [2.0,  TC2P5,  -TC1P5,  -TC1P5,   TC2P5,   2.0  ],
         [2.0, -TC2P5,  -TC1P5,   TC1P5,   TC2P5,  -2.0  ],
         [2.0, -TC1P5,   TC2P5,   TC2P5,  -TC1P5,   2.0  ]],
    ),

    # -----------------------------------------------------------------------
    # Reflection / horizontal groups  Cnh  (9 groups: C2h … C10h)
    # Cn axis + σh.  Even n → inversion centre (g/u irreps).
    # Odd n → no inversion (′/″ irreps).
    # -----------------------------------------------------------------------

    # C2h
    PointGroup(
        Label(Class.Ch, 2), 4, 1, {2: 1}, {}, 1,
        [OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(1, O(E.sigma, OPlane.h))],
        [I(M.A, IParity.g), I(M.B, IParity.g),
         I(M.A, IParity.u), I(M.B, IParity.u)],
        [[1.0,  1.0,  1.0,  1.0],
         [1.0, -1.0,  1.0, -1.0],
         [1.0,  1.0, -1.0, -1.0],
         [1.0, -1.0, -1.0,  1.0]],
    ),

    # C3h
    PointGroup(
        Label(Class.Ch, 3), 6, 0, {3: 1}, {3: 1}, 1,
        [OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(1, O(E.sigma, OPlane.h)),
         OperationLabelCount(2, O(E.S, 3))],
        [I(M.A, IPrime.Single), I(M.A, IPrime.Double),
         I(M.E, IPrime.Single), I(M.E, IPrime.Double)],
        [[1.0,  1.0,  1.0,  1.0],
         [1.0,  1.0, -1.0, -1.0],
         [2.0, -1.0,  2.0, -1.0],
         [2.0, -1.0, -2.0,  1.0]],
    ),

    # C4h
    PointGroup(
        Label(Class.Ch, 4), 8, 1, {4: 1, 2: 1}, {4: 1}, 1,
        [OperationLabelCount(2, O(E.C, 4)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(2, O(E.S, 4)),
         OperationLabelCount(1, O(E.sigma, OPlane.h))],
        [I(M.A, IParity.g), I(M.B, IParity.g), I(M.E, IParity.g),
         I(M.A, IParity.u), I(M.B, IParity.u), I(M.E, IParity.u)],
        [[1.0,  1.0,  1.0,  1.0,  1.0,  1.0],
         [1.0, -1.0,  1.0,  1.0, -1.0,  1.0],
         [2.0,  0.0, -2.0,  2.0,  0.0, -2.0],
         [1.0,  1.0,  1.0, -1.0, -1.0, -1.0],
         [1.0, -1.0,  1.0, -1.0,  1.0, -1.0],
         [2.0,  0.0, -2.0, -2.0,  0.0,  2.0]],
    ),

    # C5h
    PointGroup(
        Label(Class.Ch, 5), 10, 0, {5: 1}, {5: 1}, 1,
        [OperationLabelCount(2, O(E.C, 5)),
         OperationLabelCount(2, O(E.C, 5, 2)),
         OperationLabelCount(1, O(E.sigma, OPlane.h)),
         OperationLabelCount(2, O(E.S, 5)),
         OperationLabelCount(2, O(E.S, 5, 3))],
        [I(M.A, IPrime.Single), I(M.A, IPrime.Double),
         I(M.E, 1, IPrime.Single), I(M.E, 1, IPrime.Double),
         I(M.E, 2, IPrime.Single), I(M.E, 2, IPrime.Double)],
        [[1.0,  1.0,     1.0,    1.0,    1.0,    1.0   ],
         [1.0,  1.0,     1.0,   -1.0,   -1.0,   -1.0   ],
         [2.0,  TC2P5,  -TC1P5,  2.0,    TC2P5, -TC1P5  ],
         [2.0,  TC2P5,  -TC1P5, -2.0,   -TC2P5,  TC1P5  ],
         [2.0, -TC1P5,   TC2P5,  2.0,   -TC1P5,  TC2P5  ],
         [2.0, -TC1P5,   TC2P5, -2.0,    TC1P5, -TC2P5  ]],
    ),

    # C6h
    PointGroup(
        Label(Class.Ch, 6), 12, 1, {6: 1, 3: 1, 2: 1}, {6: 1, 3: 1}, 1,
        [OperationLabelCount(2, O(E.C, 6)),
         OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(2, O(E.C, 2)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(2, O(E.S, 6)),
         OperationLabelCount(2, O(E.S, 3)),
         OperationLabelCount(1, O(E.sigma, OPlane.h))],
        [I(M.A, IParity.g), I(M.B, IParity.g),
         I(M.E, 1, IParity.g), I(M.E, 2, IParity.g),
         I(M.A, IParity.u), I(M.B, IParity.u),
         I(M.E, 1, IParity.u), I(M.E, 2, IParity.u)],
        [[1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0],
         [1.0, -1.0,  1.0, -1.0,  1.0,  1.0, -1.0, -1.0],
         [2.0,  1.0, -1.0, -2.0,  2.0, -1.0,  1.0, -2.0],
         [2.0, -1.0, -1.0,  2.0,  2.0, -1.0, -1.0,  2.0],
         [1.0,  1.0,  1.0,  1.0, -1.0, -1.0, -1.0, -1.0],
         [1.0, -1.0,  1.0, -1.0, -1.0, -1.0,  1.0,  1.0],
         [2.0,  1.0, -1.0, -2.0, -2.0,  1.0, -1.0,  2.0],
         [2.0, -1.0, -1.0,  2.0, -2.0,  1.0,  1.0, -2.0]],
    ),

    # C7h
    PointGroup(
        Label(Class.Ch, 7), 14, 0, {7: 1}, {7: 1}, 1,
        [OperationLabelCount(2, O(E.C, 7)),
         OperationLabelCount(2, O(E.C, 7, 2)),
         OperationLabelCount(2, O(E.C, 7, 3)),
         OperationLabelCount(1, O(E.sigma, OPlane.h)),
         OperationLabelCount(2, O(E.S, 7)),
         OperationLabelCount(2, O(E.S, 7, 3)),
         OperationLabelCount(2, O(E.S, 7, 5))],
        [I(M.A, IPrime.Single), I(M.A, IPrime.Double),
         I(M.E, 1, IPrime.Single), I(M.E, 1, IPrime.Double),
         I(M.E, 2, IPrime.Single), I(M.E, 2, IPrime.Double),
         I(M.E, 3, IPrime.Single), I(M.E, 3, IPrime.Double)],
        [[1.0,  1.0,      1.0,     1.0,    1.0,     1.0,    1.0,     1.0   ],
         [1.0,  1.0,      1.0,     1.0,   -1.0,    -1.0,   -1.0,    -1.0   ],
         [2.0,  TC2P7,   -TC3P7,  -TC1P7,  2.0,    TC2P7,  -TC1P7,  -TC3P7 ],
         [2.0,  TC2P7,   -TC3P7,  -TC1P7, -2.0,   -TC2P7,   TC1P7,   TC3P7 ],
         [2.0, -TC3P7,   -TC1P7,   TC2P7,  2.0,   -TC3P7,   TC2P7,  -TC1P7 ],
         [2.0, -TC3P7,   -TC1P7,   TC2P7, -2.0,    TC3P7,  -TC2P7,   TC1P7 ],
         [2.0, -TC1P7,    TC2P7,  -TC3P7,  2.0,   -TC1P7,  -TC3P7,   TC2P7 ],
         [2.0, -TC1P7,    TC2P7,  -TC3P7, -2.0,    TC1P7,   TC3P7,  -TC2P7 ]],
    ),

    # C8h
    PointGroup(
        Label(Class.Ch, 8), 16, 1, {8: 1, 4: 1, 2: 1}, {8: 1, 4: 1}, 1,
        [OperationLabelCount(2, O(E.C, 8)),
         OperationLabelCount(2, O(E.C, 4)),
         OperationLabelCount(2, O(E.C, 8, 3)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(2, O(E.S, 8)),
         OperationLabelCount(2, O(E.S, 4)),
         OperationLabelCount(2, O(E.S, 8, 3)),
         OperationLabelCount(1, O(E.sigma, OPlane.h))],
        [I(M.A, IParity.g), I(M.B, IParity.g),
         I(M.E, 1, IParity.g), I(M.E, 2, IParity.g), I(M.E, 3, IParity.g),
         I(M.A, IParity.u), I(M.B, IParity.u),
         I(M.E, 1, IParity.u), I(M.E, 2, IParity.u), I(M.E, 3, IParity.u)],
        [[1.0,  1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0  ],
         [1.0, -1.0,    1.0,   -1.0,    1.0,    1.0,   -1.0,    1.0,   -1.0,    1.0  ],
         [2.0,  TC1P4,  0.0,  -TC1P4,  -2.0,    2.0,  -TC1P4,  0.0,    TC1P4,  -2.0  ],
         [2.0,  0.0,   -2.0,   0.0,    2.0,    2.0,    0.0,   -2.0,    0.0,    2.0  ],
         [2.0, -TC1P4,  0.0,   TC1P4,  -2.0,    2.0,   TC1P4,  0.0,   -TC1P4,  -2.0  ],
         [1.0,  1.0,    1.0,    1.0,    1.0,   -1.0,   -1.0,   -1.0,   -1.0,   -1.0  ],
         [1.0, -1.0,    1.0,   -1.0,    1.0,   -1.0,    1.0,   -1.0,    1.0,   -1.0  ],
         [2.0,  TC1P4,  0.0,  -TC1P4,  -2.0,   -2.0,   TC1P4,  0.0,   -TC1P4,   2.0  ],
         [2.0,  0.0,   -2.0,   0.0,    2.0,   -2.0,    0.0,    2.0,    0.0,   -2.0  ],
         [2.0, -TC1P4,  0.0,   TC1P4,  -2.0,   -2.0,  -TC1P4,  0.0,    TC1P4,   2.0  ]],
    ),

    # C9h
    PointGroup(
        Label(Class.Ch, 9), 18, 0, {9: 1, 3: 1}, {9: 1, 3: 1}, 1,
        [OperationLabelCount(2, O(E.C, 9)),
         OperationLabelCount(2, O(E.C, 9, 2)),
         OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(2, O(E.C, 9, 4)),
         OperationLabelCount(1, O(E.sigma, OPlane.h)),
         OperationLabelCount(2, O(E.S, 9)),
         OperationLabelCount(2, O(E.S, 3)),
         OperationLabelCount(2, O(E.S, 9, 5)),
         OperationLabelCount(2, O(E.S, 9, 7))],
        [I(M.A, IPrime.Single), I(M.A, IPrime.Double),
         I(M.E, 1, IPrime.Single), I(M.E, 1, IPrime.Double),
         I(M.E, 2, IPrime.Single), I(M.E, 2, IPrime.Double),
         I(M.E, 3, IPrime.Single), I(M.E, 3, IPrime.Double),
         I(M.E, 4, IPrime.Single), I(M.E, 4, IPrime.Double)],
        [[1.0,  1.0,     1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0   ],
         [1.0,  1.0,     1.0,    1.0,    1.0,   -1.0,   -1.0,   -1.0,   -1.0,   -1.0   ],
         [2.0,  TC2P9,   TC4P9,  -1.0,  -TC1P9,  2.0,    TC2P9,  -1.0,  -TC1P9,  TC4P9  ],
         [2.0,  TC2P9,   TC4P9,  -1.0,  -TC1P9, -2.0,   -TC2P9,   1.0,   TC1P9, -TC4P9  ],
         [2.0,  TC4P9,  -TC1P9,  -1.0,   TC2P9,  2.0,    TC4P9,  -1.0,   TC2P9, -TC1P9  ],
         [2.0,  TC4P9,  -TC1P9,  -1.0,   TC2P9, -2.0,   -TC4P9,   1.0,  -TC2P9,  TC1P9  ],
         [2.0,  -1.0,   -1.0,    2.0,   -1.0,   2.0,    -1.0,   2.0,    -1.0,   -1.0   ],
         [2.0,  -1.0,   -1.0,    2.0,   -1.0,  -2.0,     1.0,  -2.0,     1.0,    1.0   ],
         [2.0, -TC1P9,   TC2P9,  -1.0,   TC4P9,  2.0,   -TC1P9,  -1.0,   TC4P9,  TC2P9  ],
         [2.0, -TC1P9,   TC2P9,  -1.0,   TC4P9, -2.0,    TC1P9,   1.0,  -TC4P9, -TC2P9  ]],
    ),

    # C10h
    PointGroup(
        Label(Class.Ch, 10), 20, 1, {10: 1, 5: 1, 2: 1}, {10: 1, 5: 1}, 1,
        [OperationLabelCount(2, O(E.C, 10)),
         OperationLabelCount(2, O(E.C, 5)),
         OperationLabelCount(2, O(E.C, 10, 3)),
         OperationLabelCount(2, O(E.C, 5, 2)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(2, O(E.S, 10)),
         OperationLabelCount(2, O(E.S, 5)),
         OperationLabelCount(2, O(E.S, 10, 3)),
         OperationLabelCount(2, O(E.S, 5, 2)),
         OperationLabelCount(1, O(E.sigma, OPlane.h))],
        [I(M.A, IParity.g), I(M.B, IParity.g),
         I(M.E, 1, IParity.g), I(M.E, 2, IParity.g),
         I(M.E, 3, IParity.g), I(M.E, 4, IParity.g),
         I(M.A, IParity.u), I(M.B, IParity.u),
         I(M.E, 1, IParity.u), I(M.E, 2, IParity.u),
         I(M.E, 3, IParity.u), I(M.E, 4, IParity.u)],
        [[1.0,  1.0,     1.0,     1.0,     1.0,     1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0  ],
         [1.0, -1.0,     1.0,    -1.0,     1.0,    -1.0,    1.0,    1.0,   -1.0,    1.0,   -1.0,   -1.0  ],
         [2.0,  TC1P5,   TC2P5,  -TC2P5,  -TC1P5,  -2.0,    2.0,  -TC1P5, -TC2P5,  TC2P5,  TC1P5,  -2.0  ],
         [2.0,  TC2P5,  -TC1P5,  -TC1P5,   TC2P5,   2.0,    2.0,   TC2P5, -TC1P5, -TC1P5,  TC2P5,   2.0  ],
         [2.0, -TC2P5,  -TC1P5,   TC1P5,   TC2P5,  -2.0,    2.0,   TC2P5,  TC1P5, -TC1P5, -TC2P5,  -2.0  ],
         [2.0, -TC1P5,   TC2P5,   TC2P5,  -TC1P5,   2.0,    2.0,  -TC1P5,  TC2P5,  TC2P5, -TC1P5,   2.0  ],
         [1.0,  1.0,     1.0,     1.0,     1.0,     1.0,   -1.0,   -1.0,   -1.0,   -1.0,   -1.0,   -1.0  ],
         [1.0, -1.0,     1.0,    -1.0,     1.0,    -1.0,   -1.0,   -1.0,    1.0,   -1.0,    1.0,    1.0  ],
         [2.0,  TC1P5,   TC2P5,  -TC2P5,  -TC1P5,  -2.0,   -2.0,   TC1P5,  TC2P5, -TC2P5, -TC1P5,   2.0  ],
         [2.0,  TC2P5,  -TC1P5,  -TC1P5,   TC2P5,   2.0,   -2.0,  -TC2P5,  TC1P5,  TC1P5, -TC2P5,  -2.0  ],
         [2.0, -TC2P5,  -TC1P5,   TC1P5,   TC2P5,  -2.0,   -2.0,  -TC2P5, -TC1P5,  TC1P5,  TC2P5,   2.0  ],
         [2.0, -TC1P5,   TC2P5,   TC2P5,  -TC1P5,   2.0,   -2.0,   TC1P5, -TC2P5, -TC2P5,  TC1P5,  -2.0  ]],
    ),

    # -----------------------------------------------------------------------
    # Pyramidal groups  Cnv  (9 groups: C2v … C10v)
    # Cn axis + n vertical mirrors σv.  Examples: C2v = water, C3v = ammonia.
    # Even n → σv and σd planes; odd n → all σv equivalent.
    # -----------------------------------------------------------------------

    # C2v
    PointGroup(
        Label(Class.Cv, 2), 4, 0, {2: 1}, {}, 2,
        [OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(1, O(E.sigma, OPlane.v)),
         OperationLabelCount(1, O(E.sigma, OPlane.v, OPrime.Single))],
        [I(M.A, 1), I(M.A, 2), I(M.B, 1), I(M.B, 2)],
        [[1.0,  1.0,  1.0,  1.0],
         [1.0,  1.0, -1.0, -1.0],
         [1.0, -1.0,  1.0, -1.0],
         [1.0, -1.0, -1.0,  1.0]],
    ),

    # C3v
    PointGroup(
        Label(Class.Cv, 3), 6, 0, {3: 1}, {}, 3,
        [OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(3, O(E.sigma, OPlane.v))],
        [I(M.A, 1), I(M.A, 2), I(M.E)],
        [[1.0,  1.0,  1.0],
         [1.0,  1.0, -1.0],
         [2.0, -1.0,  0.0]],
    ),

    # C4v
    PointGroup(
        Label(Class.Cv, 4), 8, 0, {4: 1, 2: 1}, {}, 4,
        [OperationLabelCount(2, O(E.C, 4)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(2, O(E.sigma, OPlane.v)),
         OperationLabelCount(2, O(E.sigma, OPlane.d))],
        [I(M.A, 1), I(M.A, 2), I(M.B, 1), I(M.B, 2), I(M.E)],
        [[1.0,  1.0,  1.0,  1.0,  1.0],
         [1.0,  1.0,  1.0, -1.0, -1.0],
         [1.0, -1.0,  1.0,  1.0, -1.0],
         [1.0, -1.0,  1.0, -1.0,  1.0],
         [2.0,  0.0, -2.0,  0.0,  0.0]],
    ),

    # C5v
    PointGroup(
        Label(Class.Cv, 5), 10, 0, {5: 1}, {}, 5,
        [OperationLabelCount(2, O(E.C, 5)),
         OperationLabelCount(2, O(E.C, 5, 2)),
         OperationLabelCount(5, O(E.sigma, OPlane.v))],
        [I(M.A, 1), I(M.A, 2), I(M.E, 1), I(M.E, 2)],
        [[1.0,  1.0,    1.0,    1.0],
         [1.0,  1.0,    1.0,   -1.0],
         [2.0,  TC2P5, -TC1P5,  0.0],
         [2.0, -TC1P5,  TC2P5,  0.0]],
    ),

    # C6v
    PointGroup(
        Label(Class.Cv, 6), 12, 0, {6: 1, 3: 1, 2: 1}, {}, 6,
        [OperationLabelCount(2, O(E.C, 6)),
         OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(3, O(E.sigma, OPlane.v)),
         OperationLabelCount(3, O(E.sigma, OPlane.d))],
        [I(M.A, 1), I(M.A, 2), I(M.B, 1), I(M.B, 2), I(M.E, 1), I(M.E, 2)],
        [[1.0,  1.0,  1.0,  1.0,  1.0,  1.0],
         [1.0,  1.0,  1.0,  1.0, -1.0, -1.0],
         [1.0, -1.0,  1.0, -1.0,  1.0, -1.0],
         [1.0, -1.0,  1.0, -1.0, -1.0,  1.0],
         [2.0,  1.0, -1.0, -2.0,  0.0,  0.0],
         [2.0, -1.0, -1.0,  2.0,  0.0,  0.0]],
    ),

    # C7v
    PointGroup(
        Label(Class.Cv, 7), 14, 0, {7: 1}, {}, 7,
        [OperationLabelCount(2, O(E.C, 7)),
         OperationLabelCount(2, O(E.C, 7, 2)),
         OperationLabelCount(2, O(E.C, 7, 3)),
         OperationLabelCount(7, O(E.sigma, OPlane.v))],
        [I(M.A, 1), I(M.A, 2), I(M.E, 1), I(M.E, 2), I(M.E, 3)],
        [[1.0,  1.0,     1.0,     1.0,    1.0],
         [1.0,  1.0,     1.0,     1.0,   -1.0],
         [2.0,  TC2P7,  -TC3P7,  -TC1P7,  0.0],
         [2.0, -TC3P7,  -TC1P7,   TC2P7,  0.0],
         [2.0, -TC1P7,   TC2P7,  -TC3P7,  0.0]],
    ),

    # C8v
    PointGroup(
        Label(Class.Cv, 8), 16, 0, {8: 1, 4: 1, 2: 1}, {}, 8,
        [OperationLabelCount(2, O(E.C, 8)),
         OperationLabelCount(2, O(E.C, 4)),
         OperationLabelCount(2, O(E.C, 8, 3)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(4, O(E.sigma, OPlane.v)),
         OperationLabelCount(4, O(E.sigma, OPlane.d))],
        [I(M.A, 1), I(M.A, 2), I(M.B, 1), I(M.B, 2),
         I(M.E, 1), I(M.E, 2), I(M.E, 3)],
        [[1.0,  1.0,    1.0,    1.0,    1.0,    1.0,    1.0],
         [1.0,  1.0,    1.0,    1.0,    1.0,   -1.0,   -1.0],
         [1.0, -1.0,    1.0,   -1.0,    1.0,    1.0,   -1.0],
         [1.0, -1.0,    1.0,   -1.0,    1.0,   -1.0,    1.0],
         [2.0,  TC1P4,  0.0,  -TC1P4,  -2.0,    0.0,    0.0],
         [2.0,  0.0,   -2.0,   0.0,    2.0,    0.0,    0.0],
         [2.0, -TC1P4,  0.0,   TC1P4,  -2.0,    0.0,    0.0]],
    ),

    # C9v
    PointGroup(
        Label(Class.Cv, 9), 18, 0, {9: 1, 3: 1}, {}, 9,
        [OperationLabelCount(2, O(E.C, 9)),
         OperationLabelCount(2, O(E.C, 9, 2)),
         OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(2, O(E.C, 9, 4)),
         OperationLabelCount(9, O(E.sigma, OPlane.v))],
        [I(M.A, 1), I(M.A, 2), I(M.E, 1), I(M.E, 2), I(M.E, 3), I(M.E, 4)],
        [[1.0,  1.0,     1.0,    1.0,    1.0,    1.0],
         [1.0,  1.0,     1.0,    1.0,    1.0,   -1.0],
         [2.0,  TC2P9,   TC4P9,  -1.0,  -TC1P9,  0.0],
         [2.0,  TC4P9,  -TC1P9,  -1.0,   TC2P9,  0.0],
         [2.0,  -1.0,   -1.0,    2.0,   -1.0,   0.0],
         [2.0, -TC1P9,   TC2P9,  -1.0,   TC4P9,  0.0]],
    ),

    # C10v
    PointGroup(
        Label(Class.Cv, 10), 20, 0, {10: 1, 5: 1, 2: 1}, {}, 10,
        [OperationLabelCount(2, O(E.C, 10)),
         OperationLabelCount(2, O(E.C, 5)),
         OperationLabelCount(2, O(E.C, 10, 3)),
         OperationLabelCount(2, O(E.C, 5, 2)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(2, O(E.sigma, OPlane.v)),
         OperationLabelCount(2, O(E.sigma, OPlane.d))],
        [I(M.A, 1), I(M.A, 2), I(M.B, 1), I(M.B, 2),
         I(M.E, 1), I(M.E, 2), I(M.E, 3), I(M.E, 4)],
        [[1.0,  1.0,     1.0,     1.0,     1.0,     1.0,    1.0,    1.0],
         [1.0,  1.0,     1.0,     1.0,     1.0,     1.0,   -1.0,   -1.0],
         [1.0, -1.0,     1.0,    -1.0,     1.0,    -1.0,    1.0,   -1.0],
         [1.0, -1.0,     1.0,    -1.0,     1.0,    -1.0,   -1.0,    1.0],
         [2.0,  TC1P5,   TC2P5,  -TC2P5,  -TC1P5,  -2.0,   0.0,    0.0],
         [2.0,  TC2P5,  -TC1P5,  -TC1P5,   TC2P5,   2.0,   0.0,    0.0],
         [2.0, -TC2P5,  -TC1P5,   TC1P5,   TC2P5,  -2.0,   0.0,    0.0],
         [2.0, -TC1P5,   TC2P5,   TC2P5,  -TC1P5,   2.0,   0.0,    0.0]],
    ),


    # -----------------------------------------------------------------------
    # Improper rotation groups  Sn  (4 groups: S4, S6, S8, S10)
    # Only an Sn axis; no independent σ or Cn.  S6 and S10 have inversion.
    # -----------------------------------------------------------------------

    # S4
    PointGroup(
        Label(Class.S, 4), 4, 0, {2: 1}, {4: 1}, 0,
        [OperationLabelCount(2, O(E.S, 4)),
         OperationLabelCount(1, O(E.C, 2))],
        [I(M.A), I(M.B), I(M.E)],
        [[1.0,  1.0,  1.0],
         [1.0, -1.0,  1.0],
         [2.0,  0.0, -2.0]],
    ),

    # S6
    PointGroup(
        Label(Class.S, 6), 6, 1, {3: 1}, {6: 1}, 0,
        [OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(2, O(E.S, 6))],
        [I(M.A, IParity.g), I(M.E, IParity.g),
         I(M.A, IParity.u), I(M.E, IParity.u)],
        [[1.0,  1.0,  1.0,  1.0],
         [2.0, -1.0,  2.0, -1.0],
         [1.0,  1.0, -1.0, -1.0],
         [2.0, -1.0, -2.0,  1.0]],
    ),

    # S8
    PointGroup(
        Label(Class.S, 8), 8, 0, {4: 1, 2: 1}, {8: 1}, 0,
        [OperationLabelCount(2, O(E.S, 8)),
         OperationLabelCount(2, O(E.C, 4)),
         OperationLabelCount(2, O(E.S, 8, 3)),
         OperationLabelCount(1, O(E.C, 2))],
        [I(M.A), I(M.B), I(M.E, 1), I(M.E, 2), I(M.E, 3)],
        [[1.0,  1.0,    1.0,    1.0,    1.0 ],
         [1.0, -1.0,    1.0,   -1.0,    1.0 ],
         [2.0,  TC1P4,  0.0,  -TC1P4,  -2.0 ],
         [2.0,  0.0,   -2.0,   0.0,    2.0  ],
         [2.0, -TC1P4,  0.0,   TC1P4,  -2.0 ]],
    ),

    # S10
    PointGroup(
        Label(Class.S, 10), 10, 1, {5: 1}, {10: 1}, 0,
        [OperationLabelCount(2, O(E.C, 5)),
         OperationLabelCount(2, O(E.C, 5, 2)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(2, O(E.S, 10)),
         OperationLabelCount(2, O(E.S, 10, 3))],
        [I(M.A, IParity.g), I(M.E, 1, IParity.g), I(M.E, 2, IParity.g),
         I(M.A, IParity.u), I(M.E, 1, IParity.u), I(M.E, 2, IParity.u)],
        [[1.0,  1.0,      1.0,     1.0,  1.0,      1.0    ],
         [2.0,  TC2P5,   -TC1P5,   2.0, -TC1P5,    TC2P5  ],
         [2.0, -TC1P5,    TC2P5,   2.0,  TC2P5,   -TC1P5  ],
         [1.0,  1.0,      1.0,    -1.0, -1.0,     -1.0    ],
         [2.0,  TC2P5,   -TC1P5,  -2.0,  TC1P5,   -TC2P5  ],
         [2.0, -TC1P5,    TC2P5,  -2.0, -TC2P5,    TC1P5  ]],
    ),

    # -----------------------------------------------------------------------
    # Dihedral groups  Dn  (9 groups: D2 … D10)
    # Cn axis + n horizontal C2 axes; no mirrors.  Chiral.
    # Even n → two sets of C2′/C2″; odd n → one set of n C2′.
    # -----------------------------------------------------------------------

    # D2
    PointGroup(
        Label(Class.D, 2), 4, 0, {2: 3}, {}, 0,
        [OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(1, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(1, O(E.C, 2, OPrime.Double))],
        [I(M.A), I(M.B, 1), I(M.B, 2), I(M.B, 3)],
        [[1.0,  1.0,  1.0,  1.0],
         [1.0,  1.0, -1.0, -1.0],
         [1.0, -1.0, -1.0,  1.0],
         [1.0, -1.0,  1.0, -1.0]],
    ),

    # D3
    PointGroup(
        Label(Class.D, 3), 6, 0, {3: 1, 2: 3}, {}, 0,
        [OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(3, O(E.C, 2, OPrime.Single))],
        [I(M.A, 1), I(M.A, 2), I(M.E)],
        [[1.0,  1.0,  1.0],
         [1.0,  1.0, -1.0],
         [2.0, -1.0,  0.0]],
    ),

    # D4
    PointGroup(
        Label(Class.D, 4), 8, 0, {4: 1, 2: 5}, {}, 0,
        [OperationLabelCount(2, O(E.C, 4)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(2, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(2, O(E.C, 2, OPrime.Double))],
        [I(M.A, 1), I(M.A, 2), I(M.B, 1), I(M.B, 2), I(M.E)],
        [[1.0,  1.0,  1.0,  1.0,  1.0],
         [1.0,  1.0,  1.0, -1.0, -1.0],
         [1.0, -1.0,  1.0,  1.0, -1.0],
         [1.0, -1.0,  1.0, -1.0,  1.0],
         [2.0,  0.0, -2.0,  0.0,  0.0]],
    ),

    # D5
    PointGroup(
        Label(Class.D, 5), 10, 0, {5: 1, 2: 5}, {}, 0,
        [OperationLabelCount(2, O(E.C, 5)),
         OperationLabelCount(2, O(E.C, 5, 2)),
         OperationLabelCount(5, O(E.C, 2, OPrime.Single))],
        [I(M.A, 1), I(M.A, 2), I(M.E, 1), I(M.E, 2)],
        [[1.0,  1.0,    1.0,    1.0],
         [1.0,  1.0,    1.0,   -1.0],
         [2.0,  TC2P5, -TC1P5,  0.0],
         [2.0, -TC1P5,  TC2P5,  0.0]],
    ),

    # D6
    PointGroup(
        Label(Class.D, 6), 12, 0, {6: 1, 3: 1, 2: 7}, {}, 0,
        [OperationLabelCount(2, O(E.C, 6)),
         OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(3, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(3, O(E.C, 2, OPrime.Double))],
        [I(M.A, 1), I(M.A, 2), I(M.B, 1), I(M.B, 2), I(M.E, 1), I(M.E, 2)],
        [[1.0,  1.0,  1.0,  1.0,  1.0,  1.0],
         [1.0,  1.0,  1.0,  1.0, -1.0, -1.0],
         [1.0, -1.0,  1.0, -1.0,  1.0, -1.0],
         [1.0, -1.0,  1.0, -1.0, -1.0,  1.0],
         [2.0,  1.0, -1.0, -2.0,  0.0,  0.0],
         [2.0, -1.0, -1.0,  2.0,  0.0,  0.0]],
    ),

    # D7
    PointGroup(
        Label(Class.D, 7), 14, 0, {7: 1, 2: 7}, {}, 0,
        [OperationLabelCount(2, O(E.C, 7)),
         OperationLabelCount(2, O(E.C, 7, 2)),
         OperationLabelCount(2, O(E.C, 7, 3)),
         OperationLabelCount(7, O(E.C, 2, OPrime.Single))],
        [I(M.A, 1), I(M.A, 2), I(M.E, 1), I(M.E, 2), I(M.E, 3)],
        [[1.0,  1.0,      1.0,     1.0,    1.0],
         [1.0,  1.0,      1.0,     1.0,   -1.0],
         [2.0,  TC2P7,   -TC3P7,  -TC1P7,  0.0],
         [2.0, -TC3P7,   -TC1P7,   TC2P7,  0.0],
         [2.0, -TC1P7,    TC2P7,  -TC3P7,  0.0]],
    ),

    # D8
    PointGroup(
        Label(Class.D, 8), 16, 0, {8: 1, 4: 1, 2: 9}, {}, 0,
        [OperationLabelCount(2, O(E.C, 8)),
         OperationLabelCount(2, O(E.C, 4)),
         OperationLabelCount(2, O(E.C, 8, 3)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(4, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(4, O(E.C, 2, OPrime.Double))],
        [I(M.A, 1), I(M.A, 2), I(M.B, 1), I(M.B, 2),
         I(M.E, 1), I(M.E, 2), I(M.E, 3)],
        [[1.0,  1.0,    1.0,    1.0,    1.0,    1.0,    1.0],
         [1.0,  1.0,    1.0,    1.0,    1.0,   -1.0,   -1.0],
         [1.0, -1.0,    1.0,   -1.0,    1.0,    1.0,   -1.0],
         [1.0, -1.0,    1.0,   -1.0,    1.0,   -1.0,    1.0],
         [2.0,  TC1P4,  0.0,  -TC1P4,  -2.0,    0.0,    0.0],
         [2.0,  0.0,   -2.0,   0.0,    2.0,    0.0,    0.0],
         [2.0, -TC1P4,  0.0,   TC1P4,  -2.0,    0.0,    0.0]],
    ),

    # D9
    PointGroup(
        Label(Class.D, 9), 18, 0, {9: 1, 3: 1, 2: 9}, {}, 0,
        [OperationLabelCount(2, O(E.C, 9)),
         OperationLabelCount(2, O(E.C, 9, 2)),
         OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(2, O(E.C, 9, 4)),
         OperationLabelCount(9, O(E.C, 2, OPrime.Single))],
        [I(M.A, 1), I(M.A, 2), I(M.E, 1), I(M.E, 2), I(M.E, 3), I(M.E, 4)],
        [[1.0,  1.0,     1.0,    1.0,    1.0,    1.0],
         [1.0,  1.0,     1.0,    1.0,    1.0,   -1.0],
         [2.0,  TC2P9,   TC4P9,  -1.0,  -TC1P9,  0.0],
         [2.0,  TC4P9,  -TC1P9,  -1.0,   TC2P9,  0.0],
         [2.0,  -1.0,   -1.0,    2.0,   -1.0,   0.0],
         [2.0, -TC1P9,   TC2P9,  -1.0,   TC4P9,  0.0]],
    ),

    # D10
    PointGroup(
        Label(Class.D, 10), 20, 0, {10: 1, 5: 1, 2: 11}, {}, 0,
        [OperationLabelCount(2, O(E.C, 10)),
         OperationLabelCount(2, O(E.C, 5)),
         OperationLabelCount(2, O(E.C, 10, 3)),
         OperationLabelCount(2, O(E.C, 5, 2)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(5, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(5, O(E.C, 2, OPrime.Double))],
        [I(M.A, 1), I(M.A, 2), I(M.B, 1), I(M.B, 2),
         I(M.E, 1), I(M.E, 2), I(M.E, 3), I(M.E, 4)],
        [[1.0,  1.0,     1.0,     1.0,     1.0,     1.0,    1.0,    1.0],
         [1.0,  1.0,     1.0,     1.0,     1.0,     1.0,   -1.0,   -1.0],
         [1.0, -1.0,     1.0,    -1.0,     1.0,    -1.0,    1.0,   -1.0],
         [1.0, -1.0,     1.0,    -1.0,     1.0,    -1.0,   -1.0,    1.0],
         [2.0,  TC1P5,   TC2P5,  -TC2P5,  -TC1P5,  -2.0,   0.0,    0.0],
         [2.0,  TC2P5,  -TC1P5,  -TC1P5,   TC2P5,   2.0,   0.0,    0.0],
         [2.0, -TC2P5,  -TC1P5,   TC1P5,   TC2P5,  -2.0,   0.0,    0.0],
         [2.0, -TC1P5,   TC2P5,   TC2P5,  -TC1P5,   2.0,   0.0,    0.0]],
    ),

    # -----------------------------------------------------------------------
    # Prismatic groups  Dnh  (9 groups: D2h … D10h)
    # Dn + σh; the "prism" groups.  Even n → inversion + g/u; odd n → ′/″.
    # Examples: D2h = ethylene, D3h = BF3, D6h = benzene.
    # -----------------------------------------------------------------------

    # D2h
    PointGroup(
        Label(Class.Dh, 2), 8, 1, {2: 3}, {}, 3,
        [OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(1, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(1, O(E.C, 2, OPrime.Double)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(1, O(E.sigma, OPlane.h)),
         OperationLabelCount(1, O(E.sigma, OPlane.v)),
         OperationLabelCount(1, O(E.sigma, OPlane.v, OPrime.Single))],
        [I(M.A, IParity.g), I(M.B, 1, IParity.g), I(M.B, 2, IParity.g), I(M.B, 3, IParity.g),
         I(M.A, IParity.u), I(M.B, 1, IParity.u), I(M.B, 2, IParity.u), I(M.B, 3, IParity.u)],
        [[1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0],
         [1.0,  1.0, -1.0, -1.0,  1.0,  1.0, -1.0, -1.0],
         [1.0, -1.0, -1.0,  1.0,  1.0, -1.0,  1.0, -1.0],
         [1.0, -1.0,  1.0, -1.0,  1.0, -1.0, -1.0,  1.0],
         [1.0,  1.0,  1.0,  1.0, -1.0, -1.0, -1.0, -1.0],
         [1.0,  1.0, -1.0, -1.0, -1.0, -1.0,  1.0,  1.0],
         [1.0, -1.0, -1.0,  1.0, -1.0,  1.0, -1.0,  1.0],
         [1.0, -1.0,  1.0, -1.0, -1.0,  1.0,  1.0, -1.0]],
    ),

    # D3h
    PointGroup(
        Label(Class.Dh, 3), 12, 0, {3: 1, 2: 3}, {3: 1}, 4,
        [OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(3, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(1, O(E.sigma, OPlane.h)),
         OperationLabelCount(2, O(E.S, 3)),
         OperationLabelCount(3, O(E.sigma, OPlane.v))],
        [I(M.A, 1, IPrime.Single), I(M.A, 1, IPrime.Double),
         I(M.A, 2, IPrime.Single), I(M.A, 2, IPrime.Double),
         I(M.E, IPrime.Single),    I(M.E, IPrime.Double)],
        [[1.0,  1.0,  1.0,  1.0,  1.0,  1.0],
         [1.0,  1.0,  1.0, -1.0, -1.0, -1.0],
         [1.0,  1.0, -1.0,  1.0,  1.0, -1.0],
         [1.0,  1.0, -1.0, -1.0, -1.0,  1.0],
         [2.0, -1.0,  0.0,  2.0, -1.0,  0.0],
         [2.0, -1.0,  0.0, -2.0,  1.0,  0.0]],
    ),

    # D4h
    PointGroup(
        Label(Class.Dh, 4), 16, 1, {4: 1, 2: 5}, {4: 1}, 5,
        [OperationLabelCount(2, O(E.C, 4)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(2, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(2, O(E.C, 2, OPrime.Double)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(2, O(E.S, 4)),
         OperationLabelCount(1, O(E.sigma, OPlane.h)),
         OperationLabelCount(2, O(E.sigma, OPlane.v)),
         OperationLabelCount(2, O(E.sigma, OPlane.d))],
        [I(M.A, 1, IParity.g), I(M.A, 2, IParity.g),
         I(M.B, 1, IParity.g), I(M.B, 2, IParity.g), I(M.E, IParity.g),
         I(M.A, 1, IParity.u), I(M.A, 2, IParity.u),
         I(M.B, 1, IParity.u), I(M.B, 2, IParity.u), I(M.E, IParity.u)],
        [[1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0],
         [1.0,  1.0,  1.0, -1.0, -1.0,  1.0,  1.0,  1.0, -1.0, -1.0],
         [1.0, -1.0,  1.0,  1.0, -1.0,  1.0, -1.0,  1.0,  1.0, -1.0],
         [1.0, -1.0,  1.0, -1.0,  1.0,  1.0, -1.0,  1.0, -1.0,  1.0],
         [2.0,  0.0, -2.0,  0.0,  0.0,  2.0,  0.0, -2.0,  0.0,  0.0],
         [1.0,  1.0,  1.0,  1.0,  1.0, -1.0, -1.0, -1.0, -1.0, -1.0],
         [1.0,  1.0,  1.0, -1.0, -1.0, -1.0, -1.0, -1.0,  1.0,  1.0],
         [1.0, -1.0,  1.0,  1.0, -1.0, -1.0,  1.0, -1.0, -1.0,  1.0],
         [1.0, -1.0,  1.0, -1.0,  1.0, -1.0,  1.0, -1.0,  1.0, -1.0],
         [2.0,  0.0, -2.0,  0.0,  0.0, -2.0,  0.0,  2.0,  0.0,  0.0]],
    ),

    # D5h
    PointGroup(
        Label(Class.Dh, 5), 20, 0, {5: 1, 2: 5}, {5: 1}, 6,
        [OperationLabelCount(2, O(E.C, 5)),
         OperationLabelCount(2, O(E.C, 5, 2)),
         OperationLabelCount(5, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(1, O(E.sigma, OPlane.h)),
         OperationLabelCount(2, O(E.S, 5)),
         OperationLabelCount(2, O(E.S, 5, 3)),
         OperationLabelCount(5, O(E.sigma, OPlane.v))],
        [I(M.A, 1, IPrime.Single), I(M.A, 1, IPrime.Double),
         I(M.A, 2, IPrime.Single), I(M.A, 2, IPrime.Double),
         I(M.E, 1, IPrime.Single), I(M.E, 1, IPrime.Double),
         I(M.E, 2, IPrime.Single), I(M.E, 2, IPrime.Double)],
        [[1.0,  1.0,      1.0,     1.0,  1.0,      1.0,     1.0,     1.0  ],
         [1.0,  1.0,      1.0,     1.0, -1.0,     -1.0,    -1.0,    -1.0  ],
         [1.0,  1.0,      1.0,    -1.0,  1.0,      1.0,     1.0,    -1.0  ],
         [1.0,  1.0,      1.0,    -1.0, -1.0,     -1.0,    -1.0,     1.0  ],
         [2.0,  TC2P5,   -TC1P5,   0.0,  2.0,      TC2P5,  -TC1P5,   0.0  ],
         [2.0,  TC2P5,   -TC1P5,   0.0, -2.0,     -TC2P5,   TC1P5,   0.0  ],
         [2.0, -TC1P5,    TC2P5,   0.0,  2.0,     -TC1P5,   TC2P5,   0.0  ],
         [2.0, -TC1P5,    TC2P5,   0.0, -2.0,      TC1P5,  -TC2P5,   0.0  ]],
    ),

    # D6h
    PointGroup(
        Label(Class.Dh, 6), 24, 1, {6: 1, 3: 1, 2: 7}, {6: 1, 3: 1}, 7,
        [OperationLabelCount(2, O(E.C, 6)),
         OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(3, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(3, O(E.C, 2, OPrime.Double)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(2, O(E.S, 6)),
         OperationLabelCount(2, O(E.S, 3)),
         OperationLabelCount(1, O(E.sigma, OPlane.h)),
         OperationLabelCount(3, O(E.sigma, OPlane.v)),
         OperationLabelCount(3, O(E.sigma, OPlane.d))],
        [I(M.A, 1, IParity.g), I(M.A, 2, IParity.g),
         I(M.B, 1, IParity.g), I(M.B, 2, IParity.g),
         I(M.E, 1, IParity.g), I(M.E, 2, IParity.g),
         I(M.A, 1, IParity.u), I(M.A, 2, IParity.u),
         I(M.B, 1, IParity.u), I(M.B, 2, IParity.u),
         I(M.E, 1, IParity.u), I(M.E, 2, IParity.u)],
        [[1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0],
         [1.0,  1.0,  1.0,  1.0, -1.0, -1.0,  1.0,  1.0,  1.0,  1.0, -1.0, -1.0],
         [1.0, -1.0,  1.0, -1.0,  1.0, -1.0,  1.0,  1.0, -1.0, -1.0, -1.0,  1.0],
         [1.0, -1.0,  1.0, -1.0, -1.0,  1.0,  1.0,  1.0, -1.0, -1.0,  1.0, -1.0],
         [2.0,  1.0, -1.0, -2.0,  0.0,  0.0,  2.0, -1.0,  1.0, -2.0,  0.0,  0.0],
         [2.0, -1.0, -1.0,  2.0,  0.0,  0.0,  2.0, -1.0, -1.0,  2.0,  0.0,  0.0],
         [1.0,  1.0,  1.0,  1.0,  1.0,  1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0],
         [1.0,  1.0,  1.0,  1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0,  1.0,  1.0],
         [1.0, -1.0,  1.0, -1.0,  1.0, -1.0, -1.0, -1.0,  1.0,  1.0,  1.0, -1.0],
         [1.0, -1.0,  1.0, -1.0, -1.0,  1.0, -1.0, -1.0,  1.0,  1.0, -1.0,  1.0],
         [2.0,  1.0, -1.0, -2.0,  0.0,  0.0, -2.0,  1.0, -1.0,  2.0,  0.0,  0.0],
         [2.0, -1.0, -1.0,  2.0,  0.0,  0.0, -2.0,  1.0,  1.0, -2.0,  0.0,  0.0]],
    ),

    # D7h
    PointGroup(
        Label(Class.Dh, 7), 28, 0, {7: 1, 2: 7}, {7: 1}, 8,
        [OperationLabelCount(2, O(E.C, 7)),
         OperationLabelCount(2, O(E.C, 7, 2)),
         OperationLabelCount(2, O(E.C, 7, 3)),
         OperationLabelCount(7, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(1, O(E.sigma, OPlane.h)),
         OperationLabelCount(2, O(E.S, 7)),
         OperationLabelCount(2, O(E.S, 7, 3)),
         OperationLabelCount(2, O(E.S, 7, 5)),
         OperationLabelCount(7, O(E.sigma, OPlane.v))],
        [I(M.A, 1, IPrime.Single), I(M.A, 1, IPrime.Double),
         I(M.A, 2, IPrime.Single), I(M.A, 2, IPrime.Double),
         I(M.E, 1, IPrime.Single), I(M.E, 1, IPrime.Double),
         I(M.E, 2, IPrime.Single), I(M.E, 2, IPrime.Double),
         I(M.E, 3, IPrime.Single), I(M.E, 3, IPrime.Double)],
        [[1.0,  1.0,      1.0,     1.0,    1.0,     1.0,    1.0,     1.0,    1.0,     1.0   ],
         [1.0,  1.0,      1.0,     1.0,    1.0,    -1.0,   -1.0,    -1.0,   -1.0,    -1.0   ],
         [1.0,  1.0,      1.0,     1.0,   -1.0,    1.0,    1.0,     1.0,    1.0,    -1.0   ],
         [1.0,  1.0,      1.0,     1.0,   -1.0,   -1.0,   -1.0,    -1.0,   -1.0,     1.0   ],
         [2.0,  TC2P7,   -TC3P7,  -TC1P7,  0.0,    2.0,    TC2P7,  -TC1P7,  -TC3P7,   0.0   ],
         [2.0,  TC2P7,   -TC3P7,  -TC1P7,  0.0,   -2.0,   -TC2P7,   TC1P7,   TC3P7,   0.0   ],
         [2.0, -TC3P7,   -TC1P7,   TC2P7,  0.0,    2.0,   -TC3P7,   TC2P7,  -TC1P7,   0.0   ],
         [2.0, -TC3P7,   -TC1P7,   TC2P7,  0.0,   -2.0,    TC3P7,  -TC2P7,   TC1P7,   0.0   ],
         [2.0, -TC1P7,    TC2P7,  -TC3P7,  0.0,    2.0,   -TC1P7,  -TC3P7,   TC2P7,   0.0   ],
         [2.0, -TC1P7,    TC2P7,  -TC3P7,  0.0,   -2.0,    TC1P7,   TC3P7,  -TC2P7,   0.0   ]],
    ),

    # D8h
    PointGroup(
        Label(Class.Dh, 8), 32, 1, {8: 1, 4: 1, 2: 9}, {8: 1, 4: 1}, 9,
        [OperationLabelCount(2, O(E.C, 8)),
         OperationLabelCount(2, O(E.C, 4)),
         OperationLabelCount(2, O(E.C, 8, 3)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(4, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(4, O(E.C, 2, OPrime.Double)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(2, O(E.S, 8)),
         OperationLabelCount(2, O(E.S, 4)),
         OperationLabelCount(2, O(E.S, 8, 3)),
         OperationLabelCount(1, O(E.sigma, OPlane.h)),
         OperationLabelCount(4, O(E.sigma, OPlane.v)),
         OperationLabelCount(4, O(E.sigma, OPlane.d))],
        [I(M.A, 1, IParity.g), I(M.A, 2, IParity.g),
         I(M.B, 1, IParity.g), I(M.B, 2, IParity.g),
         I(M.E, 1, IParity.g), I(M.E, 2, IParity.g), I(M.E, 3, IParity.g),
         I(M.A, 1, IParity.u), I(M.A, 2, IParity.u),
         I(M.B, 1, IParity.u), I(M.B, 2, IParity.u),
         I(M.E, 1, IParity.u), I(M.E, 2, IParity.u), I(M.E, 3, IParity.u)],
        [[1.0,  1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0],
         [1.0,  1.0,    1.0,    1.0,    1.0,   -1.0,   -1.0,   1.0,    1.0,    1.0,    1.0,    1.0,   -1.0,   -1.0],
         [1.0, -1.0,    1.0,   -1.0,    1.0,    1.0,   -1.0,   1.0,   -1.0,    1.0,   -1.0,    1.0,    1.0,   -1.0],
         [1.0, -1.0,    1.0,   -1.0,    1.0,   -1.0,    1.0,   1.0,   -1.0,    1.0,   -1.0,    1.0,   -1.0,    1.0],
         [2.0,  TC1P4,  0.0,  -TC1P4,  -2.0,    0.0,    0.0,   2.0,  -TC1P4,   0.0,   TC1P4,  -2.0,    0.0,    0.0],
         [2.0,  0.0,   -2.0,   0.0,    2.0,    0.0,    0.0,   2.0,    0.0,   -2.0,    0.0,    2.0,    0.0,    0.0],
         [2.0, -TC1P4,  0.0,   TC1P4,  -2.0,    0.0,    0.0,   2.0,   TC1P4,   0.0,  -TC1P4,  -2.0,    0.0,    0.0],
         [1.0,  1.0,    1.0,    1.0,    1.0,    1.0,    1.0,  -1.0,   -1.0,   -1.0,   -1.0,   -1.0,   -1.0,   -1.0],
         [1.0,  1.0,    1.0,    1.0,    1.0,   -1.0,   -1.0,  -1.0,   -1.0,   -1.0,   -1.0,   -1.0,    1.0,    1.0],
         [1.0, -1.0,    1.0,   -1.0,    1.0,    1.0,   -1.0,  -1.0,    1.0,   -1.0,    1.0,   -1.0,   -1.0,    1.0],
         [1.0, -1.0,    1.0,   -1.0,    1.0,   -1.0,    1.0,  -1.0,    1.0,   -1.0,    1.0,   -1.0,    1.0,   -1.0],
         [2.0,  TC1P4,  0.0,  -TC1P4,  -2.0,    0.0,    0.0,  -2.0,   TC1P4,   0.0,  -TC1P4,   2.0,    0.0,    0.0],
         [2.0,  0.0,   -2.0,   0.0,    2.0,    0.0,    0.0,  -2.0,    0.0,    2.0,    0.0,   -2.0,    0.0,    0.0],
         [2.0, -TC1P4,  0.0,   TC1P4,  -2.0,    0.0,    0.0,  -2.0,  -TC1P4,   0.0,   TC1P4,   2.0,    0.0,    0.0]],
    ),

    # D9h
    PointGroup(
        Label(Class.Dh, 9), 36, 0, {9: 1, 3: 1, 2: 9}, {9: 1, 3: 1}, 10,
        [OperationLabelCount(2, O(E.C, 9)),
         OperationLabelCount(2, O(E.C, 9, 2)),
         OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(2, O(E.C, 9, 4)),
         OperationLabelCount(9, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(1, O(E.sigma, OPlane.h)),
         OperationLabelCount(2, O(E.S, 9)),
         OperationLabelCount(2, O(E.S, 3)),
         OperationLabelCount(2, O(E.S, 9, 5)),
         OperationLabelCount(2, O(E.S, 9, 7)),
         OperationLabelCount(9, O(E.sigma, OPlane.v))],
        [I(M.A, 1, IPrime.Single), I(M.A, 1, IPrime.Double),
         I(M.A, 2, IPrime.Single), I(M.A, 2, IPrime.Double),
         I(M.E, 1, IPrime.Single), I(M.E, 1, IPrime.Double),
         I(M.E, 2, IPrime.Single), I(M.E, 2, IPrime.Double),
         I(M.E, 3, IPrime.Single), I(M.E, 3, IPrime.Double),
         I(M.E, 4, IPrime.Single), I(M.E, 4, IPrime.Double)],
        [[1.0,  1.0,     1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0  ],
         [1.0,  1.0,     1.0,    1.0,    1.0,    1.0,   -1.0,   -1.0,   -1.0,   -1.0,   -1.0,   -1.0  ],
         [1.0,  1.0,     1.0,    1.0,    1.0,   -1.0,    1.0,    1.0,    1.0,    1.0,    1.0,   -1.0  ],
         [1.0,  1.0,     1.0,    1.0,    1.0,   -1.0,   -1.0,   -1.0,   -1.0,   -1.0,   -1.0,    1.0  ],
         [2.0,  TC2P9,   TC4P9,  -1.0,  -TC1P9,  0.0,    2.0,    TC2P9,  -1.0,  -TC1P9,  TC4P9,   0.0  ],
         [2.0,  TC2P9,   TC4P9,  -1.0,  -TC1P9,  0.0,   -2.0,   -TC2P9,   1.0,   TC1P9, -TC4P9,   0.0  ],
         [2.0,  TC4P9,  -TC1P9,  -1.0,   TC2P9,  0.0,    2.0,    TC4P9,  -1.0,   TC2P9, -TC1P9,   0.0  ],
         [2.0,  TC4P9,  -TC1P9,  -1.0,   TC2P9,  0.0,   -2.0,   -TC4P9,   1.0,  -TC2P9,  TC1P9,   0.0  ],
         [2.0,  -1.0,   -1.0,    2.0,   -1.0,   0.0,    2.0,    -1.0,   2.0,    -1.0,   -1.0,   0.0  ],
         [2.0,  -1.0,   -1.0,    2.0,   -1.0,   0.0,   -2.0,     1.0,  -2.0,     1.0,    1.0,   0.0  ],
         [2.0, -TC1P9,   TC2P9,  -1.0,   TC4P9,  0.0,    2.0,   -TC1P9,  -1.0,   TC4P9,  TC2P9,   0.0  ],
         [2.0, -TC1P9,   TC2P9,  -1.0,   TC4P9,  0.0,   -2.0,    TC1P9,   1.0,  -TC4P9, -TC2P9,   0.0  ]],
    ),

    # D10h
    PointGroup(
        Label(Class.Dh, 10), 40, 1, {10: 1, 5: 1, 2: 11}, {10: 1, 5: 1}, 11,
        [OperationLabelCount(2, O(E.C, 10)),
         OperationLabelCount(2, O(E.C, 5)),
         OperationLabelCount(2, O(E.C, 10, 3)),
         OperationLabelCount(2, O(E.C, 5, 2)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(5, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(5, O(E.C, 2, OPrime.Double)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(2, O(E.S, 10)),
         OperationLabelCount(2, O(E.S, 5)),
         OperationLabelCount(2, O(E.S, 10, 3)),
         OperationLabelCount(2, O(E.S, 5, 2)),
         OperationLabelCount(1, O(E.sigma, OPlane.h)),
         OperationLabelCount(5, O(E.sigma, OPlane.v)),
         OperationLabelCount(5, O(E.sigma, OPlane.d))],
        [I(M.A, 1, IParity.g), I(M.A, 2, IParity.g),
         I(M.B, 1, IParity.g), I(M.B, 2, IParity.g),
         I(M.E, 1, IParity.g), I(M.E, 2, IParity.g),
         I(M.E, 3, IParity.g), I(M.E, 4, IParity.g),
         I(M.A, 1, IParity.u), I(M.A, 2, IParity.u),
         I(M.B, 1, IParity.u), I(M.B, 2, IParity.u),
         I(M.E, 1, IParity.u), I(M.E, 2, IParity.u),
         I(M.E, 3, IParity.u), I(M.E, 4, IParity.u)],
        [[1.0,  1.0,     1.0,     1.0,     1.0,     1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0  ],
         [1.0,  1.0,     1.0,     1.0,     1.0,     1.0,   -1.0,   -1.0,   1.0,    1.0,    1.0,    1.0,    1.0,    1.0,   -1.0,   -1.0  ],
         [1.0, -1.0,     1.0,    -1.0,     1.0,    -1.0,    1.0,   -1.0,   1.0,    1.0,   -1.0,    1.0,   -1.0,   -1.0,   -1.0,    1.0  ],
         [1.0, -1.0,     1.0,    -1.0,     1.0,    -1.0,   -1.0,    1.0,   1.0,    1.0,   -1.0,    1.0,   -1.0,   -1.0,    1.0,   -1.0  ],
         [2.0,  TC1P5,   TC2P5,  -TC2P5,  -TC1P5,  -2.0,    0.0,    0.0,   2.0,   -TC1P5, -TC2P5,  TC2P5,  TC1P5,  -2.0,    0.0,    0.0  ],
         [2.0,  TC2P5,  -TC1P5,  -TC1P5,   TC2P5,   2.0,    0.0,    0.0,   2.0,    TC2P5, -TC1P5, -TC1P5,  TC2P5,   2.0,    0.0,    0.0  ],
         [2.0, -TC2P5,  -TC1P5,   TC1P5,   TC2P5,  -2.0,    0.0,    0.0,   2.0,    TC2P5,  TC1P5, -TC1P5, -TC2P5,  -2.0,    0.0,    0.0  ],
         [2.0, -TC1P5,   TC2P5,   TC2P5,  -TC1P5,   2.0,    0.0,    0.0,   2.0,   -TC1P5,  TC2P5,  TC2P5, -TC1P5,   2.0,    0.0,    0.0  ],
         [1.0,  1.0,     1.0,     1.0,     1.0,     1.0,    1.0,    1.0,  -1.0,   -1.0,   -1.0,   -1.0,   -1.0,   -1.0,   -1.0,   -1.0  ],
         [1.0,  1.0,     1.0,     1.0,     1.0,     1.0,   -1.0,   -1.0,  -1.0,   -1.0,   -1.0,   -1.0,   -1.0,   -1.0,    1.0,    1.0  ],
         [1.0, -1.0,     1.0,    -1.0,     1.0,    -1.0,    1.0,   -1.0,  -1.0,   -1.0,    1.0,   -1.0,    1.0,    1.0,    1.0,   -1.0  ],
         [1.0, -1.0,     1.0,    -1.0,     1.0,    -1.0,   -1.0,    1.0,  -1.0,   -1.0,    1.0,   -1.0,    1.0,    1.0,   -1.0,    1.0  ],
         [2.0,  TC1P5,   TC2P5,  -TC2P5,  -TC1P5,  -2.0,    0.0,    0.0,  -2.0,    TC1P5,  TC2P5, -TC2P5, -TC1P5,   2.0,    0.0,    0.0  ],
         [2.0,  TC2P5,  -TC1P5,  -TC1P5,   TC2P5,   2.0,    0.0,    0.0,  -2.0,   -TC2P5,  TC1P5,  TC1P5, -TC2P5,  -2.0,    0.0,    0.0  ],
         [2.0, -TC2P5,  -TC1P5,   TC1P5,   TC2P5,  -2.0,    0.0,    0.0,  -2.0,   -TC2P5, -TC1P5,  TC1P5,  TC2P5,   2.0,    0.0,    0.0  ],
         [2.0, -TC1P5,   TC2P5,   TC2P5,  -TC1P5,   2.0,    0.0,    0.0,  -2.0,    TC1P5, -TC2P5, -TC2P5,  TC1P5,  -2.0,    0.0,    0.0  ]],
    ),

    # -----------------------------------------------------------------------
    # Antiprismatic groups  Dnd  (9 groups: D2d … D10d)
    # Dn + dihedral mirrors σd (+ S_{2n} axis).  Examples: D2d = allene,
    # D3d = staggered ethane.  Odd n → inversion centre.
    # -----------------------------------------------------------------------

    # D2d
    PointGroup(
        Label(Class.Dd, 2), 8, 0, {2: 3}, {4: 1}, 2,
        [OperationLabelCount(2, O(E.S, 4)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(2, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(2, O(E.sigma, OPlane.d))],
        [I(M.A, 1), I(M.A, 2), I(M.B, 1), I(M.B, 2), I(M.E)],
        [[1.0,  1.0,  1.0,  1.0,  1.0],
         [1.0,  1.0,  1.0, -1.0, -1.0],
         [1.0, -1.0,  1.0,  1.0, -1.0],
         [1.0, -1.0,  1.0, -1.0,  1.0],
         [2.0,  0.0, -2.0,  0.0,  0.0]],
    ),

    # D3d
    PointGroup(
        Label(Class.Dd, 3), 12, 1, {3: 1, 2: 3}, {6: 1}, 3,
        [OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(3, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(2, O(E.S, 6)),
         OperationLabelCount(3, O(E.sigma, OPlane.d))],
        [I(M.A, 1, IParity.g), I(M.A, 2, IParity.g), I(M.E, IParity.g),
         I(M.A, 1, IParity.u), I(M.A, 2, IParity.u), I(M.E, IParity.u)],
        [[1.0,  1.0,  1.0,  1.0,  1.0,  1.0],
         [1.0,  1.0, -1.0,  1.0,  1.0, -1.0],
         [2.0, -1.0,  0.0,  2.0, -1.0,  0.0],
         [1.0,  1.0,  1.0, -1.0, -1.0, -1.0],
         [1.0,  1.0, -1.0, -1.0, -1.0,  1.0],
         [2.0, -1.0,  0.0, -2.0,  1.0,  0.0]],
    ),

    # D4d
    PointGroup(
        Label(Class.Dd, 4), 16, 0, {4: 1, 2: 5}, {8: 1}, 4,
        [OperationLabelCount(2, O(E.S, 8)),
         OperationLabelCount(2, O(E.C, 4)),
         OperationLabelCount(2, O(E.S, 8, 3)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(4, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(4, O(E.sigma, OPlane.d))],
        [I(M.A, 1), I(M.A, 2), I(M.B, 1), I(M.B, 2), I(M.E, 1), I(M.E, 2), I(M.E, 3)],
        [[1.0,    1.0,    1.0,    1.0,   1.0,   1.0,   1.0],
         [1.0,    1.0,    1.0,    1.0,   1.0,  -1.0,  -1.0],
         [1.0,   -1.0,    1.0,   -1.0,   1.0,   1.0,  -1.0],
         [1.0,   -1.0,    1.0,   -1.0,   1.0,  -1.0,   1.0],
         [2.0,   TC1P4,   0.0,  -TC1P4, -2.0,   0.0,   0.0],
         [2.0,   0.0,    -2.0,   0.0,   2.0,   0.0,   0.0],
         [2.0,  -TC1P4,   0.0,   TC1P4, -2.0,   0.0,   0.0]],
    ),

    # D5d
    PointGroup(
        Label(Class.Dd, 5), 20, 1, {5: 1, 2: 5}, {10: 1}, 5,
        [OperationLabelCount(2, O(E.C, 5)),
         OperationLabelCount(2, O(E.C, 5, 2)),
         OperationLabelCount(5, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(2, O(E.S, 10)),
         OperationLabelCount(2, O(E.S, 10, 3)),
         OperationLabelCount(5, O(E.sigma, OPlane.d))],
        [I(M.A, 1, IParity.g), I(M.A, 2, IParity.g), I(M.E, 1, IParity.g), I(M.E, 2, IParity.g),
         I(M.A, 1, IParity.u), I(M.A, 2, IParity.u), I(M.E, 1, IParity.u), I(M.E, 2, IParity.u)],
        [[1.0,    1.0,    1.0,   1.0,   1.0,   1.0,   1.0,   1.0],
         [1.0,    1.0,    1.0,  -1.0,   1.0,   1.0,   1.0,  -1.0],
         [2.0,   TC2P5, -TC1P5,  0.0,   2.0, -TC1P5,  TC2P5, 0.0],
         [2.0,  -TC1P5,  TC2P5,  0.0,   2.0,  TC2P5, -TC1P5, 0.0],
         [1.0,    1.0,    1.0,   1.0,  -1.0,  -1.0,  -1.0,  -1.0],
         [1.0,    1.0,    1.0,  -1.0,  -1.0,  -1.0,  -1.0,   1.0],
         [2.0,   TC2P5, -TC1P5,  0.0,  -2.0,  TC1P5, -TC2P5, 0.0],
         [2.0,  -TC1P5,  TC2P5,  0.0,  -2.0, -TC2P5,  TC1P5, 0.0]],
    ),

    # D6d
    PointGroup(
        Label(Class.Dd, 6), 24, 0, {6: 1, 3: 1, 2: 7}, {12: 1, 4: 1}, 6,
        [OperationLabelCount(2, O(E.S, 12)),
         OperationLabelCount(2, O(E.C, 6)),
         OperationLabelCount(2, O(E.S, 4)),
         OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(2, O(E.S, 12, 5)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(6, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(6, O(E.sigma, OPlane.d))],
        [I(M.A, 1), I(M.A, 2), I(M.B, 1), I(M.B, 2),
         I(M.E, 1), I(M.E, 2), I(M.E, 3), I(M.E, 4), I(M.E, 5)],
        [[1.0,    1.0,   1.0,   1.0,   1.0,    1.0,   1.0,   1.0,   1.0],
         [1.0,    1.0,   1.0,   1.0,   1.0,    1.0,   1.0,  -1.0,  -1.0],
         [1.0,   -1.0,   1.0,  -1.0,   1.0,   -1.0,   1.0,   1.0,  -1.0],
         [1.0,   -1.0,   1.0,  -1.0,   1.0,   -1.0,   1.0,  -1.0,   1.0],
         [2.0,  TC1P6,   1.0,   0.0,  -1.0, -TC1P6,  -2.0,   0.0,   0.0],
         [2.0,    1.0,  -1.0,  -2.0,  -1.0,    1.0,   2.0,   0.0,   0.0],
         [2.0,    0.0,  -2.0,   0.0,   2.0,    0.0,  -2.0,   0.0,   0.0],
         [2.0,   -1.0,  -1.0,   2.0,  -1.0,   -1.0,   2.0,   0.0,   0.0],
         [2.0, -TC1P6,   1.0,   0.0,  -1.0,  TC1P6,  -2.0,   0.0,   0.0]],
    ),

    # D7d
    PointGroup(
        Label(Class.Dd, 7), 28, 1, {7: 1, 2: 7}, {14: 1}, 7,
        [OperationLabelCount(2, O(E.C, 7)),
         OperationLabelCount(2, O(E.C, 7, 2)),
         OperationLabelCount(2, O(E.C, 7, 3)),
         OperationLabelCount(7, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(2, O(E.S, 14)),
         OperationLabelCount(2, O(E.S, 14, 3)),
         OperationLabelCount(2, O(E.S, 14, 5)),
         OperationLabelCount(7, O(E.sigma, OPlane.d))],
        [I(M.A, 1, IParity.g), I(M.A, 2, IParity.g), I(M.E, 1, IParity.g),
         I(M.E, 2, IParity.g), I(M.E, 3, IParity.g),
         I(M.A, 1, IParity.u), I(M.A, 2, IParity.u), I(M.E, 1, IParity.u),
         I(M.E, 2, IParity.u), I(M.E, 3, IParity.u)],
        [[1.0,    1.0,     1.0,     1.0,   1.0,    1.0,    1.0,    1.0,    1.0,   1.0],
         [1.0,    1.0,     1.0,     1.0,  -1.0,    1.0,    1.0,    1.0,    1.0,  -1.0],
         [2.0,  TC2P7,  -TC3P7,  -TC1P7,   0.0,   2.0,  -TC1P7, -TC3P7,  TC2P7,  0.0],
         [2.0, -TC3P7,  -TC1P7,   TC2P7,   0.0,   2.0,   TC2P7, -TC1P7, -TC3P7,  0.0],
         [2.0, -TC1P7,   TC2P7,  -TC3P7,   0.0,   2.0,  -TC3P7,  TC2P7, -TC1P7,  0.0],
         [1.0,    1.0,     1.0,     1.0,   1.0,   -1.0,   -1.0,   -1.0,   -1.0,  -1.0],
         [1.0,    1.0,     1.0,     1.0,  -1.0,   -1.0,   -1.0,   -1.0,   -1.0,   1.0],
         [2.0,  TC2P7,  -TC3P7,  -TC1P7,   0.0,  -2.0,   TC1P7,  TC3P7, -TC2P7,  0.0],
         [2.0, -TC3P7,  -TC1P7,   TC2P7,   0.0,  -2.0,  -TC2P7,  TC1P7,  TC3P7,  0.0],
         [2.0, -TC1P7,   TC2P7,  -TC3P7,   0.0,  -2.0,   TC3P7, -TC2P7,  TC1P7,  0.0]],
    ),

    # D8d
    PointGroup(
        Label(Class.Dd, 8), 32, 0, {8: 1, 4: 1, 2: 9}, {16: 2}, 8,
        [OperationLabelCount(2, O(E.S, 16)),
         OperationLabelCount(2, O(E.C, 8)),
         OperationLabelCount(2, O(E.S, 16, 3)),
         OperationLabelCount(2, O(E.C, 4)),
         OperationLabelCount(2, O(E.S, 16, 5)),
         OperationLabelCount(2, O(E.C, 8, 3)),
         OperationLabelCount(2, O(E.S, 16, 7)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(8, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(8, O(E.sigma, OPlane.d))],
        [I(M.A, 1), I(M.A, 2), I(M.B, 1), I(M.B, 2),
         I(M.E, 1), I(M.E, 2), I(M.E, 3), I(M.E, 4), I(M.E, 5), I(M.E, 6), I(M.E, 7)],
        [[1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,   1.0,   1.0],
         [1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,  -1.0,  -1.0],
         [1.0,   -1.0,    1.0,   -1.0,    1.0,   -1.0,    1.0,   -1.0,   1.0,   1.0,  -1.0],
         [1.0,   -1.0,    1.0,   -1.0,    1.0,   -1.0,    1.0,   -1.0,   1.0,  -1.0,   1.0],
         [2.0,  TC1P8,  TC1P4,  TC3P8,   0.0,  -TC3P8, -TC1P4, -TC1P8,  -2.0,   0.0,   0.0],
         [2.0,  TC1P4,   0.0,  -TC1P4,  -2.0,  -TC1P4,   0.0,   TC1P4,   2.0,   0.0,   0.0],
         [2.0,  TC3P8, -TC1P4, -TC1P8,   0.0,   TC1P8,  TC1P4, -TC3P8,  -2.0,   0.0,   0.0],
         [2.0,   0.0,   -2.0,    0.0,    2.0,    0.0,   -2.0,    0.0,    2.0,   0.0,   0.0],
         [2.0, -TC3P8, -TC1P4,  TC1P8,   0.0,  -TC1P8,  TC1P4,  TC3P8,  -2.0,   0.0,   0.0],
         [2.0, -TC1P4,   0.0,   TC1P4,  -2.0,   TC1P4,   0.0,  -TC1P4,   2.0,   0.0,   0.0],
         [2.0, -TC1P8,  TC1P4, -TC3P8,   0.0,   TC3P8, -TC1P4,  TC1P8,  -2.0,   0.0,   0.0]],
    ),

    # D9d
    PointGroup(
        Label(Class.Dd, 9), 36, 1, {9: 1, 2: 9}, {18: 1, 6: 1}, 9,
        [OperationLabelCount(2, O(E.C, 9)),
         OperationLabelCount(2, O(E.C, 9, 2)),
         OperationLabelCount(2, O(E.C, 3)),
         OperationLabelCount(2, O(E.C, 9, 4)),
         OperationLabelCount(9, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(2, O(E.S, 18)),
         OperationLabelCount(2, O(E.S, 6)),
         OperationLabelCount(2, O(E.S, 18, 5)),
         OperationLabelCount(2, O(E.S, 18, 7)),
         OperationLabelCount(9, O(E.sigma, OPlane.d))],
        [I(M.A, 1, IParity.g), I(M.A, 2, IParity.g), I(M.E, 1, IParity.g),
         I(M.E, 2, IParity.g), I(M.E, 3, IParity.g), I(M.E, 4, IParity.g),
         I(M.A, 1, IParity.u), I(M.A, 2, IParity.u), I(M.E, 1, IParity.u),
         I(M.E, 2, IParity.u), I(M.E, 3, IParity.u), I(M.E, 4, IParity.u)],
        [[1.0,    1.0,    1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0],
         [1.0,    1.0,    1.0,   1.0,   1.0,  -1.0,   1.0,   1.0,   1.0,   1.0,   1.0,  -1.0],
         [2.0,  TC2P9,  TC4P9,  -1.0, -TC1P9,  0.0,  2.0, -TC1P9,  -1.0,  TC4P9, TC2P9,  0.0],
         [2.0,  TC4P9, -TC1P9,  -1.0,  TC2P9,  0.0,  2.0,  TC2P9,  -1.0, -TC1P9, TC4P9,  0.0],
         [2.0,   -1.0,   -1.0,   2.0,   -1.0,  0.0,  2.0,   -1.0,   2.0,   -1.0,  -1.0,  0.0],
         [2.0, -TC1P9,  TC2P9,  -1.0,  TC4P9,  0.0,  2.0,  TC4P9,  -1.0,  TC2P9,-TC1P9,  0.0],
         [1.0,    1.0,    1.0,   1.0,   1.0,   1.0,  -1.0,  -1.0,  -1.0,  -1.0,  -1.0,  -1.0],
         [1.0,    1.0,    1.0,   1.0,   1.0,  -1.0,  -1.0,  -1.0,  -1.0,  -1.0,  -1.0,   1.0],
         [2.0,  TC2P9,  TC4P9,  -1.0, -TC1P9,  0.0, -2.0,  TC1P9,   1.0, -TC4P9,-TC2P9,  0.0],
         [2.0,  TC4P9, -TC1P9,  -1.0,  TC2P9,  0.0, -2.0, -TC2P9,   1.0,  TC1P9,-TC4P9,  0.0],
         [2.0,   -1.0,   -1.0,   2.0,   -1.0,  0.0, -2.0,   1.0,   -2.0,   1.0,   1.0,   0.0],
         [2.0, -TC1P9,  TC2P9,  -1.0,  TC4P9,  0.0, -2.0, -TC4P9,   1.0, -TC2P9, TC1P9,  0.0]],
    ),

    # D10d
    PointGroup(
        Label(Class.Dd, 10), 40, 0, {10: 1, 5: 1, 2: 11}, {20: 1}, 10,
        [OperationLabelCount(2, O(E.S, 20)),
         OperationLabelCount(2, O(E.C, 10)),
         OperationLabelCount(2, O(E.S, 20, 3)),
         OperationLabelCount(2, O(E.C, 5)),
         OperationLabelCount(2, O(E.S, 4)),
         OperationLabelCount(2, O(E.C, 10, 3)),
         OperationLabelCount(2, O(E.S, 20, 7)),
         OperationLabelCount(2, O(E.C, 5, 2)),
         OperationLabelCount(2, O(E.S, 20, 9)),
         OperationLabelCount(1, O(E.C, 2)),
         OperationLabelCount(10, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(10, O(E.sigma, OPlane.d))],
        [I(M.A, 1), I(M.A, 2), I(M.B, 1), I(M.B, 2),
         I(M.E, 1), I(M.E, 2), I(M.E, 3), I(M.E, 4), I(M.E, 5),
         I(M.E, 6), I(M.E, 7), I(M.E, 8), I(M.E, 9)],
        [[1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,   1.0,   1.0,   1.0],
         [1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,   1.0,  -1.0,  -1.0],
         [1.0,   -1.0,    1.0,   -1.0,    1.0,   -1.0,    1.0,   -1.0,   1.0,   -1.0,   1.0,   1.0,  -1.0],
         [1.0,   -1.0,    1.0,   -1.0,    1.0,   -1.0,    1.0,   -1.0,   1.0,   -1.0,   1.0,  -1.0,   1.0],
         [2.0,  TC1P10, TC1P5, TC3P10,  TC2P5,   0.0,  -TC2P5, -TC3P10, -TC1P5, -TC1P10, -2.0,  0.0,  0.0],
         [2.0,  TC1P5,  TC2P5, -TC2P5, -TC1P5,  -2.0,  -TC1P5, -TC2P5,  TC2P5,   TC1P5,  2.0,  0.0,  0.0],
         [2.0,  TC3P10, -TC2P5, -TC1P10, -TC1P5,  0.0,   TC1P5,  TC1P10, TC2P5,  -TC3P10, -2.0, 0.0,  0.0],
         [2.0,  TC2P5, -TC1P5,  -TC1P5,  TC2P5,   2.0,   TC2P5,  -TC1P5, -TC1P5,  TC2P5,  2.0,  0.0,  0.0],
         [2.0,   0.0,   -2.0,    0.0,    2.0,    0.0,   -2.0,    0.0,    2.0,    0.0,   -2.0,  0.0,  0.0],
         [2.0, -TC2P5, -TC1P5,   TC1P5,  TC2P5,  -2.0,   TC2P5,  TC1P5, -TC1P5, -TC2P5,  2.0,  0.0,  0.0],
         [2.0, -TC3P10, -TC2P5,  TC1P10, -TC1P5,  0.0,   TC1P5, -TC1P10, TC2P5,  TC3P10, -2.0,  0.0,  0.0],
         [2.0, -TC1P5,  TC2P5,   TC2P5, -TC1P5,   2.0,  -TC1P5,  TC2P5,  TC2P5,  -TC1P5,  2.0,  0.0,  0.0],
         [2.0, -TC1P10, TC1P5, -TC3P10,  TC2P5,   0.0,  -TC2P5,  TC3P10, -TC1P5,  TC1P10, -2.0, 0.0,  0.0]],
    ),

    # -----------------------------------------------------------------------
    # Polyhedral groups  (7 groups: T, Td, Th, O, Oh, I, Ih)
    # No single principal axis; symmetry based on the Platonic solid geometry.
    # These cannot be generated by the axial formula, so they are hardcoded.
    # T/Td/Th → tetrahedral (methane, neopentane).
    # O/Oh    → octahedral  (SF6, [PtCl6]^2-).
    # I/Ih    → icosahedral (C60 fullerene).
    # -----------------------------------------------------------------------

    # T ─ chiral tetrahedral symmetry
    PointGroup(
        Label(Class.T), 12, 0, {3: 4, 2: 3}, {}, 0,
        [OperationLabelCount(8, O(E.C, 3)),
         OperationLabelCount(3, O(E.C, 2))],
        [I(M.A), I(M.E), I(M.T)],
        [[1.0,  1.0,  1.0],
         [2.0, -1.0,  2.0],
         [3.0,  0.0, -1.0]],
    ),

    # Td ─ achiral tetrahedral symmetry
    PointGroup(
        Label(Class.Td), 24, 0, {3: 4, 2: 3}, {4: 3}, 6,
        [OperationLabelCount(8, O(E.C, 3)),
         OperationLabelCount(3, O(E.C, 2)),
         OperationLabelCount(6, O(E.S, 4)),
         OperationLabelCount(6, O(E.sigma, OPlane.d))],
        [I(M.A, 1), I(M.A, 2), I(M.E), I(M.T, 1), I(M.T, 2)],
        [[1.0,  1.0,  1.0,  1.0,  1.0],
         [1.0,  1.0,  1.0, -1.0, -1.0],
         [2.0, -1.0,  2.0,  0.0,  0.0],
         [3.0,  0.0, -1.0,  1.0, -1.0],
         [3.0,  0.0, -1.0, -1.0,  1.0]],
    ),

    # Th ─ pyritohedral symmetry
    PointGroup(
        Label(Class.Th), 24, 1, {3: 4, 2: 3}, {6: 4}, 3,
        [OperationLabelCount(8, O(E.C, 3)),
         OperationLabelCount(3, O(E.C, 2)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(8, O(E.S, 6)),
         OperationLabelCount(3, O(E.sigma, OPlane.h))],
        [I(M.A, IParity.g), I(M.E, IParity.g), I(M.T, IParity.g),
         I(M.A, IParity.u), I(M.E, IParity.u), I(M.T, IParity.u)],
        [[1.0,  1.0,  1.0,  1.0,  1.0,  1.0],
         [2.0, -1.0,  2.0,  2.0, -1.0,  2.0],
         [3.0,  0.0, -1.0,  3.0,  0.0, -1.0],
         [1.0,  1.0,  1.0, -1.0, -1.0, -1.0],
         [2.0, -1.0,  2.0, -2.0,  1.0, -2.0],
         [3.0,  0.0, -1.0, -3.0,  0.0,  1.0]],
    ),

    # O ─ chiral octahedral symmetry
    PointGroup(
        Label(Class.O), 24, 0, {4: 3, 3: 4, 2: 9}, {}, 0,
        [OperationLabelCount(8, O(E.C, 3)),
         OperationLabelCount(3, O(E.C, 2)),
         OperationLabelCount(6, O(E.C, 4)),
         OperationLabelCount(6, O(E.C, 2, OPrime.Single))],
        [I(M.A, 1), I(M.A, 2), I(M.E), I(M.T, 1), I(M.T, 2)],
        [[1.0,  1.0,  1.0,  1.0,  1.0],
         [1.0,  1.0,  1.0, -1.0, -1.0],
         [2.0, -1.0,  2.0,  0.0,  0.0],
         [3.0,  0.0, -1.0,  1.0, -1.0],
         [3.0,  0.0, -1.0, -1.0,  1.0]],
    ),

    # Oh ─ achiral octahedral symmetry
    PointGroup(
        Label(Class.Oh), 48, 1, {4: 3, 3: 4, 2: 9}, {6: 4, 4: 3}, 9,
        [OperationLabelCount(8, O(E.C, 3)),
         OperationLabelCount(3, O(E.C, 2)),
         OperationLabelCount(6, O(E.C, 4)),
         OperationLabelCount(6, O(E.C, 2, OPrime.Single)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(8, O(E.S, 6)),
         OperationLabelCount(3, O(E.sigma, OPlane.h)),
         OperationLabelCount(6, O(E.S, 4)),
         OperationLabelCount(6, O(E.sigma, OPlane.d))],
        [I(M.A, 1, IParity.g), I(M.A, 2, IParity.g), I(M.E, IParity.g),
         I(M.T, 1, IParity.g), I(M.T, 2, IParity.g),
         I(M.A, 1, IParity.u), I(M.A, 2, IParity.u), I(M.E, IParity.u),
         I(M.T, 1, IParity.u), I(M.T, 2, IParity.u)],
        [[1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0],
         [1.0,  1.0,  1.0, -1.0, -1.0,  1.0,  1.0,  1.0, -1.0, -1.0],
         [2.0, -1.0,  2.0,  0.0,  0.0,  2.0, -1.0,  2.0,  0.0,  0.0],
         [3.0,  0.0, -1.0,  1.0, -1.0,  3.0,  0.0, -1.0,  1.0, -1.0],
         [3.0,  0.0, -1.0, -1.0,  1.0,  3.0,  0.0, -1.0, -1.0,  1.0],
         [1.0,  1.0,  1.0,  1.0,  1.0, -1.0, -1.0, -1.0, -1.0, -1.0],
         [1.0,  1.0,  1.0, -1.0, -1.0, -1.0, -1.0, -1.0,  1.0,  1.0],
         [2.0, -1.0,  2.0,  0.0,  0.0, -2.0,  1.0, -2.0,  0.0,  0.0],
         [3.0,  0.0, -1.0,  1.0, -1.0, -3.0,  0.0,  1.0, -1.0,  1.0],
         [3.0,  0.0, -1.0, -1.0,  1.0, -3.0,  0.0,  1.0,  1.0, -1.0]],
    ),

    # I ─ chiral icosahedral symmetry
    PointGroup(
        Label(Class.I), 60, 0, {5: 6, 3: 10, 2: 15}, {}, 0,
        [OperationLabelCount(12, O(E.C, 5)),
         OperationLabelCount(12, O(E.C, 5, 2)),
         OperationLabelCount(20, O(E.C, 3)),
         OperationLabelCount(15, O(E.C, 2))],
        [I(M.A), I(M.T, 1), I(M.T, 2), I(M.G), I(M.H)],
        [[1.0,  1.0,     1.0,    1.0,  1.0],
         [3.0,  TC1P5, -TC2P5,  0.0, -1.0],
         [3.0, -TC2P5,  TC1P5,  0.0, -1.0],
         [4.0, -1.0,   -1.0,    1.0,  0.0],
         [5.0,  0.0,    0.0,   -1.0,  1.0]],
    ),

    # Ih ─ achiral icosahedral symmetry
    PointGroup(
        Label(Class.Ih), 120, 1, {5: 6, 3: 10, 2: 15}, {10: 6, 6: 10}, 15,
        [OperationLabelCount(12, O(E.C, 5)),
         OperationLabelCount(12, O(E.C, 5, 2)),
         OperationLabelCount(20, O(E.C, 3)),
         OperationLabelCount(15, O(E.C, 2)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(12, O(E.S, 10)),
         OperationLabelCount(12, O(E.S, 10, 3)),
         OperationLabelCount(20, O(E.S, 6)),
         OperationLabelCount(15, O(E.sigma))],
        [I(M.A, IParity.g), I(M.T, 1, IParity.g), I(M.T, 2, IParity.g),
         I(M.G, IParity.g), I(M.H, IParity.g),
         I(M.A, IParity.u), I(M.T, 1, IParity.u), I(M.T, 2, IParity.u),
         I(M.G, IParity.u), I(M.H, IParity.u)],
        [[1.0,    1.0,     1.0,    1.0,   1.0,   1.0,    1.0,     1.0,    1.0,   1.0],
         [3.0,   TC1P5,  -TC2P5,   0.0,  -1.0,  3.0,  -TC2P5,   TC1P5,   0.0,  -1.0],
         [3.0,  -TC2P5,   TC1P5,   0.0,  -1.0,  3.0,   TC1P5,  -TC2P5,   0.0,  -1.0],
         [4.0,   -1.0,    -1.0,    1.0,   0.0,  4.0,   -1.0,    -1.0,    1.0,   0.0],
         [5.0,    0.0,     0.0,   -1.0,   1.0,  5.0,    0.0,     0.0,   -1.0,   1.0],
         [1.0,    1.0,     1.0,    1.0,   1.0, -1.0,   -1.0,    -1.0,   -1.0,  -1.0],
         [3.0,   TC1P5,  -TC2P5,   0.0,  -1.0, -3.0,   TC2P5,  -TC1P5,   0.0,   1.0],
         [3.0,  -TC2P5,   TC1P5,   0.0,  -1.0, -3.0,  -TC1P5,   TC2P5,   0.0,   1.0],
         [4.0,   -1.0,    -1.0,    1.0,   0.0, -4.0,    1.0,     1.0,   -1.0,   0.0],
         [5.0,    0.0,     0.0,   -1.0,   1.0, -5.0,    0.0,     0.0,    1.0,  -1.0]],
    ),

    # -----------------------------------------------------------------------
    # Linear groups  (2 groups: C∞v, D∞h)
    # Infinite-order rotation axis C∞.  Handled specially: degree 0 = ∞.
    # C∞v: linear, no inversion (e.g. HCN, CO).
    # D∞h: linear, with inversion (e.g. CO2, H2, N2).
    # -----------------------------------------------------------------------

    # C∞v ─ linear with a mirror plane (no inversion)
    PointGroup(
        Label(Class.Cinfv), 0, 0, {DEGREE_INF: 1}, {}, 0,
        [OperationLabelCount(2, O(E.C, DEGREE_INF)),
         OperationLabelCount(COUNT_INF, O(E.sigma, OPlane.v))],
        [],
        [],
    ),

    # D∞h ─ linear with inversion symmetry
    PointGroup(
        Label(Class.Dinfh), 0, 1, {DEGREE_INF: 1}, {DEGREE_INF: 1}, 0,
        [OperationLabelCount(2, O(E.C, DEGREE_INF)),
         OperationLabelCount(COUNT_INF, O(E.sigma, OPlane.v)),
         OperationLabelCount(1, O(E.I)),
         OperationLabelCount(2, O(E.S, DEGREE_INF)),
         OperationLabelCount(COUNT_INF, O(E.C, 2, OPrime.Single))],
        [],
        [],
    ),

]
