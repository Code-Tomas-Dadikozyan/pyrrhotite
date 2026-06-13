# Example script

The repository ships a single runnable script, [`example_usage.py`](https://github.com/datomic117/pyrrhotite/blob/main/example_usage.py),
that tours every major feature of the package — point-group determination,
character-table generation and export, idealized-structure generation, the
pretty-printers, and (optionally) the 3-D visualizer.

!!! tip "Run it after installing"
    It reads from the bundled sample molecules, so it works straight after a
    plain install — no files to download:

    ```bash
    pip install pyrrhotite
    python example_usage.py
    ```

    Sections 13–14 open the interactive viewer; they auto-skip unless you
    installed the optional extras with `pip install 'pyrrhotite[vis]'`.

The full script is reproduced below (kept in sync with the copy in the
repository on every docs build). You can also
[view or download it on GitHub](https://github.com/datomic117/pyrrhotite/blob/main/example_usage.py).

```python title="example_usage.py"
--8<-- "example_usage.py"
```
