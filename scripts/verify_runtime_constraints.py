"""Validate the versioned Windows runtime constraints file.

This deliberately uses only the standard library so it can run before the
project environment is installed.  It checks that the constraints are pinned,
unique, and cover every direct runtime dependency used by the package.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


_PINNED = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)==([^\s#]+)$")
_REQUIRED = {
    "akshare",
    "anyio",
    "cachetools",
    "httpx",
    "mcp",
    "orjson",
    "pydantic",
    "pydantic-settings",
    "tenacity",
}


def validate(path: Path) -> list[str]:
    if not path.is_file():
        raise ValueError(f"constraints file not found: {path}")

    versions: dict[str, str] = {}
    errors: list[str] = []
    for number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = _PINNED.fullmatch(line)
        if not match:
            errors.append(f"line {number}: expected an exact name==version pin")
            continue
        name, version = match.groups()
        key = name.lower().replace("_", "-")
        if key in versions:
            errors.append(f"line {number}: duplicate constraint for {name}")
        versions[key] = version

    missing = sorted(name for name in _REQUIRED if name not in versions)
    errors.extend(f"missing direct runtime dependency: {name}" for name in missing)
    if errors:
        raise ValueError("; ".join(errors))
    return sorted(versions)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Windows runtime constraints")
    parser.add_argument("path", nargs="?", default="constraints-windows-py313.txt")
    args = parser.parse_args()
    names = validate(Path(args.path))
    print(f"valid runtime constraints: {len(names)} pinned packages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
