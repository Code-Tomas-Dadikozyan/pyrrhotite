# Glossary

A short reference for the symmetry and group-theory terms used throughout these
docs. Many of these terms also appear with a dotted underline elsewhere on the
site — hover over them for a one-line reminder.

### Point group

The complete set of symmetry operations that leave a molecule's geometry
unchanged. Every molecule belongs to exactly one point group, written as a
[Schoenflies symbol](#schoenflies-symbol) such as C₂ᵥ or D₆ₕ. This is the
central quantity `pyrrhotite` computes.

### Symmetry operation

A geometric transformation — a rotation, reflection, inversion, or improper
rotation — that maps a molecule onto an indistinguishable copy of itself.

### Symmetry element

The geometric entity a symmetry operation acts around: a rotation **axis**, a
mirror **plane**, or the inversion **centre**.

### Proper rotation (Cₙ)

A rotation by 360°/n about an axis that leaves the molecule unchanged. The
largest n is the *principal axis* and sets the molecule's orientation.

### Reflection (σ)

A mirror operation through a plane. Labelled σₕ (horizontal, perpendicular to
the principal axis), σᵥ (vertical, containing it), or σd (dihedral, a vertical
plane bisecting two C₂ axes).

### Inversion (i)

The operation that sends every atom at position **r** to **−r** through a
central point (the inversion centre).

### Improper rotation (Sₙ)

A rotation by 360°/n followed by a reflection through the plane perpendicular to
that axis — a single combined operation.

### Schoenflies symbol

The notation `pyrrhotite` uses for point groups (C₂ᵥ, D₆ₕ, T_d, O_h, …), common
in chemistry and spectroscopy. The alternative
[Hermann–Mauguin](#hermannmauguin-notation) notation is more common in
crystallography.

### Hermann–Mauguin notation

The crystallographic "international" notation for symmetry groups (e.g. *mmm*,
*4/mmm*). `pyrrhotite` does **not** use it — it works entirely in Schoenflies
symbols.

### Character table

The compact table that summarises a point group: its
[irreducible representations](#irrep-irreducible-representation), the characters
(traces) of each operation class, and the basis functions that transform under
each irrep. `pyrrhotite` can generate one for any of the 18 Schoenflies classes.

### Irrep (irreducible representation)

A fundamental "symmetry species" of a point group — one row of the
[character table](#character-table). Each molecular orbital, vibration, or
rotation belongs to exactly one irrep, which is what makes irreps useful for
predicting IR/Raman activity and orbital mixing.

### Character

The trace of the transformation matrix representing a symmetry operation in a
given irrep — the numbers that fill the body of a
[character table](#character-table).

### Basis function

A coordinate (x, y, z), rotation (Rx, Ry, Rz), or quadratic term (x², xy, …)
listed against the irrep it transforms as — used to read off selection rules and
orbital symmetries.

### Conjugacy class

A set of symmetry operations that are equivalent under the group's own symmetry
(e.g. the two rotations C₃ and C₃² of C₃ᵥ form one class "2C₃"). Character tables
have one column per class, not one per operation.

### Rotor class

A classification of a molecule by the degeneracy of its
[principal moments of inertia](#principal-moments-of-inertia) — *Linear*,
*Spherical Top*, *Prolate Symmetric Top*, *Oblate Symmetric Top*, or *Asymmetric
Top*. `pyrrhotite` determines this first to narrow the symmetry search.

### Principal moments of inertia

The three eigenvalues of the molecule's inertia tensor (Iₐ ≤ I_b ≤ I_c). Their
pattern of equalities determines the [rotor class](#rotor-class).

### Principal axes

The eigenvectors of the inertia tensor — the natural body-fixed axis frame in
which the inertia tensor is diagonal.

### `.xyz` file

A plain-text molecular geometry format: an atom count, a comment line, then one
`element x y z` line per atom (coordinates in Ångströms). The standard input to
`pyrrhotite`.
