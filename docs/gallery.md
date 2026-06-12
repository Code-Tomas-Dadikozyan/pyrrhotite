# Examples gallery

Every row in this table was produced by running `pyrrhotite` on one of its
[bundled sample molecules](user-guide.md#sample-molecules) — nothing here is
hand-written. You can reproduce any line yourself:

```python
from pyrrhotite import load_sample, Symmetry

sym = Symmetry(load_sample("benzene"))
print(sym.point_group.label.name)   # "D6h"
print(sym.rotor_class.name)         # "OblateSymmetricTop"
print(sym.point_group.order)        # 24  (number of symmetry operations)
```

The molecules are ordered roughly from least to most symmetric, by the number
of symmetry operations in the detected group (the group **order**).

| Molecule | Sample name | Point group | Rotor class | Operations |
|---|---|---|---|---|
| CHFClBr | `fluorochlorobromomethane` | C1 | AsymmetricTop | 1 |
| Water | `water` | C2v | AsymmetricTop | 4 |
| *trans*-Azobenzene | `trans-azobenzene` | C2h | AsymmetricTop | 4 |
| Ammonia | `ammonia` | C3v | OblateSymmetricTop | 6 |
| Octasulfur (S₈) | `octasulfur` | D4d | OblateSymmetricTop | 16 |
| Ferrocene (staggered) | `ferrocene-staggered` | D5d | ProlateSymmetricTop | 20 |
| Ferrocene (eclipsed) | `ferrocene-eclipsed` | D5h | ProlateSymmetricTop | 20 |
| Methane | `methane` | Td | SphericalTop | 24 |
| Adamantane | `adamantane` | Td | SphericalTop | 24 |
| Benzene | `benzene` | D6h | OblateSymmetricTop | 24 |
| Tropylium | `tropylium` | D7h | OblateSymmetricTop | 28 |
| Sulfur hexafluoride | `sulfur-hexafluoride` | Oh | SphericalTop | 48 |
| Cubane | `cubane` | Oh | SphericalTop | 48 |
| Buckminsterfullerene (C₆₀) | `buckminsterfullerene` | Ih | SphericalTop | 120 |
| Carbon dioxide | `carbon-dioxide` | D∞h | Linear | ∞ |
| Hydrogen chloride | `hydrogen-chloride` | C∞v | Linear | ∞ |

!!! note "Point group and rotor class are shown exactly as `pyrrhotite` prints them"
    The **Point group** column is the literal `point_group.label.name` string,
    and **Rotor class** is the literal `RotorClass` value from
    `sym.rotor_class.name` — see
    [Rotor classification](user-guide.md#rotor-classification-and-principal-axes)
    for what each class means. The two linear molecules belong to *infinite*
    point groups (C∞ᵥ and D∞ₕ), which is why their operation count is shown as ∞.

!!! tip "See the geometry behind a result"
    Pair any row with the 3-D viewer to see the structure that produced it
    (requires `pip install 'pyrrhotite[vis]'`):

    ```python
    from pyrrhotite import visualize_sample
    visualize_sample("buckminsterfullerene")
    ```

    Or print the full character table for any of these without writing a line
    of code:

    ```bash
    pyrrhotite -g Ih          # the C60 group
    pyrrhotite -g D5d         # staggered ferrocene
    ```

!!! info "Want a different molecule?"
    These 32 samples are just a starting point. Point `pyrrhotite` at any of
    your own `.xyz` files — see [Getting Started](getting-started.md) — or build
    an idealized structure for a *named* group with
    [`generate_idealized_structure`](user-guide.md#generating-idealized-structures).
