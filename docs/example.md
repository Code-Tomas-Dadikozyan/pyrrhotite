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

## Next steps

<div class="grid cards" markdown>

-   :material-book-open-variant:{ .lg .middle } __User Guide__

    ---

    Each feature in the script, explained in depth with its full set of
    options.

    [:octicons-arrow-right-24: Open the User Guide](user-guide.md)

-   :material-image-multiple:{ .lg .middle } __Examples Gallery__

    ---

    Worked examples across point-group families, with output and rendered
    character tables.

    [:octicons-arrow-right-24: Browse the gallery](gallery.md)

-   :material-api:{ .lg .middle } __API Reference__

    ---

    The exact signatures, parameters, and return types for everything the
    script uses.

    [:octicons-arrow-right-24: Open the reference](api.md)

</div>

---

```python title="example_usage.py"
--8<-- "example_usage.py"
```
