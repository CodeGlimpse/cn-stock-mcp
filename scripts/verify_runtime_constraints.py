"""Validate the versioned Windows runtime constraints file.

The default check uses only the standard library and can run before install.
Use --installed inside the customer runtime to check the complete dependency
graph, including extras, platform markers, missing pins and installed versions.
"""

from __future__ import annotations

import argparse
from collections import deque
from importlib import metadata
import re
import tomllib
from pathlib import Path
from typing import Callable


_PINNED = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)==([^\s#]+)$")
_PROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def _canonical_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _requirements(project_path: Path) -> list[str]:
    project = tomllib.loads(project_path.read_text(encoding="utf-8"))
    return project["project"].get("dependencies", [])


def _read_pins(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise ValueError(f"constraints file not found: {path}")

    versions: dict[str, str] = {}
    errors: list[str] = []
    for number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = _PINNED.fullmatch(line)
        if not match or "*" in match.group(2):
            errors.append(f"line {number}: expected an exact name==version pin")
            continue
        name, version = match.groups()
        key = _canonical_name(name)
        if key in versions:
            errors.append(f"line {number}: duplicate constraint for {name}")
        versions[key] = version

    if errors:
        raise ValueError("; ".join(errors))
    return versions


def validate(path: Path, project_path: Path = _PROJECT) -> list[str]:
    versions = _read_pins(path)
    required = set()
    for requirement in _requirements(project_path):
        match = re.match(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)", requirement.strip())
        if not match:
            raise ValueError("invalid project dependency declaration")
        required.add(_canonical_name(match.group(1)))
    missing = sorted(required - versions.keys())
    if missing:
        raise ValueError("; ".join(f"missing direct runtime dependency: {name}" for name in missing))
    return sorted(versions)


def verify_installed_runtime(
    path: Path,
    project_path: Path = _PROJECT,
    *,
    distribution: Callable = metadata.distribution,
    environment: dict[str, str] | None = None,
) -> list[str]:
    # packaging is a declared runtime dependency. Import it here so the
    # pre-install syntax check still requires only the standard library.
    from packaging.markers import default_environment
    from packaging.requirements import Requirement
    from packaging.specifiers import SpecifierSet

    validate(path, project_path)
    pins = _read_pins(path)
    marker_environment = default_environment()
    marker_environment.update(environment or {})
    queue = deque()
    for raw in _requirements(project_path):
        requirement = Requirement(raw)
        if not requirement.marker or requirement.marker.evaluate(dict(marker_environment, extra="")):
            queue.append((requirement, "project"))

    installed = {}
    expanded_extras: dict[str, set[str]] = {}
    errors: set[str] = set()
    while queue:
        requirement, parent = queue.popleft()
        name = _canonical_name(requirement.name)
        if name not in installed:
            try:
                installed[name] = distribution(name)
            except metadata.PackageNotFoundError:
                errors.add(f"runtime dependency is not installed: {name} (required by {parent})")
                continue
        current = installed[name]
        if name not in pins:
            errors.add(f"unconstrained runtime dependency: {name} (required by {parent})")
        elif not SpecifierSet(f"=={pins[name]}").contains(current.version, prereleases=True):
            errors.add(f"installed {name}=={current.version} differs from pinned {pins[name]}")
        if requirement.url or not requirement.specifier.contains(current.version, prereleases=True):
            errors.add(f"installed {name}=={current.version} does not satisfy dependency from {parent}")

        extras = expanded_extras.get(name)
        requested_extras = set(requirement.extras)
        if extras is not None and requested_extras <= extras:
            continue
        extras = (extras or set()) | requested_extras
        expanded_extras[name] = extras
        for raw in current.requires or []:
            child = Requirement(raw)
            if child.marker and not any(
                child.marker.evaluate(dict(marker_environment, extra=extra))
                for extra in extras | {""}
            ):
                continue
            queue.append((child, name))

    if errors:
        raise ValueError("; ".join(sorted(errors)))
    return sorted(installed)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Windows runtime constraints")
    parser.add_argument("path", nargs="?", default="constraints-windows-py313.txt")
    parser.add_argument("--project", type=Path, default=_PROJECT)
    parser.add_argument("--installed", action="store_true", help="Inspect this interpreter's runtime dependency graph")
    args = parser.parse_args()
    names = validate(Path(args.path), args.project)
    print(f"valid runtime constraints: {len(names)} pinned packages")
    if args.installed:
        installed = verify_installed_runtime(Path(args.path), args.project)
        print(f"verified installed runtime: {len(installed)} dependencies, no missing pins or version conflicts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
