"""Validate that version strings in pyproject.toml, _version.py, and meta.yaml all match."""

import re


def get_version_projecttoml() -> list[int]:
    with open("pyproject.toml") as f:
        for line in f:
            m = re.search(r'version\s*=\s*"([^"]+)"', line)
            if m:
                return [int(x) for x in m.group(1).split(".")]
    raise RuntimeError("Version not found in pyproject.toml")


def get_version_versionpy() -> list[int]:
    with open("pyrrhotite/_version.py") as f:
        for line in f:
            m = re.search(r'__version__\s*=\s*"([^"]+)"', line)
            if m:
                return [int(x) for x in m.group(1).split(".")]
    raise RuntimeError("Version not found in pyrrhotite/_version.py")


def get_version_metayaml() -> list[int]:
    with open("meta.yaml") as f:
        for line in f:
            m = re.search(r'version:\s*"([^"]+)"', line)
            if m:
                return [int(x) for x in m.group(1).split(".")]
    raise RuntimeError("Version not found in meta.yaml")


if __name__ == "__main__":
    v_toml = get_version_projecttoml()
    v_py = get_version_versionpy()
    v_meta = get_version_metayaml()

    assert v_toml == v_py == v_meta, (
        f"Invalid version strings encountered: "
        f"pyproject.toml={v_toml}, _version.py={v_py}, meta.yaml={v_meta}"
    )

    print(f"Version check passed: {'.'.join(str(x) for x in v_toml)}")
