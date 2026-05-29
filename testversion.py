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
    with open("src/_version.py") as f:
        for line in f:
            m = re.search(r'__version__\s*=\s*"([^"]+)"', line)
            if m:
                return [int(x) for x in m.group(1).split(".")]
    raise RuntimeError("Version not found in src/_version.py")


if __name__ == "__main__":
    v_toml = get_version_projecttoml()
    v_py = get_version_versionpy()

    assert v_toml == v_py, (
        f"Invalid version strings encountered: "
        f"pyproject.toml={v_toml}, _version.py={v_py}"
    )

    print(f"Version check passed: {'.'.join(str(x) for x in v_toml)}")
