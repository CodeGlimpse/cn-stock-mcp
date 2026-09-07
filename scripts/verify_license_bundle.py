"""Verify dependency notices without application imports or network access.

Only the standard library is required. The root may be a source checkout or
the installed share/cn-stock-mcp directory; notice files retain their exact
upstream bytes while the constraints hash uses LF-normalized line endings.
This checks the evidence bundle, not permission to use market data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tomllib


_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA = "cn_stock_third_party_licenses_v1"
_NAME = r"[A-Za-z0-9](?:[A-Za-z0-9_.-]*[A-Za-z0-9])?"
_PIN = re.compile(rf"({_NAME})==([^\s#*]+)")
_NOTICE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.+-]*\.txt")


def _canonical_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate manifest field: {key}")
        result[key] = value
    return result


def _digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", value):
        raise ValueError(f"invalid SHA256 for {label}")
    return value.lower()


def _local_file(root: Path, path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"file escapes bundle root: {path.name}")
    if not path.is_file():
        raise ValueError(f"missing bundle file: {path.name}")
    return path


def validate(root: Path = _ROOT) -> dict:
    root = root.resolve()
    bundle = root / "third_party_licenses"
    if not bundle.resolve().is_relative_to(root):
        raise ValueError("notice directory escapes bundle root")
    manifest_path = _local_file(root, bundle / "manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    if not isinstance(manifest, dict) or manifest.get("schema") != _SCHEMA:
        raise ValueError("unsupported license manifest schema")
    if manifest.get("constraints_hash_normalization") != "lf":
        raise ValueError("constraints_hash_normalization must be lf")

    constraints_path = _local_file(root, root / "constraints-windows-py313.txt")
    constraints = constraints_path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    constraints_hash = hashlib.sha256(constraints).hexdigest()
    if _digest(manifest.get("constraints_sha256"), "constraints") != constraints_hash:
        raise ValueError("constraints SHA256 does not match the license manifest")
    pins = {}
    for number, raw in enumerate(constraints.decode("utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = _PIN.fullmatch(line)
        if match is None:
            raise ValueError(f"constraint line {number}: expected an exact name==version pin")
        name, version = match.groups()
        name = _canonical_name(name)
        if name in pins:
            raise ValueError(f"duplicate constraint: {name}")
        pins[name] = version

    project_path = _local_file(root, root / "pyproject.toml")
    project = tomllib.loads(project_path.read_text(encoding="utf-8"))
    requirements = project.get("project", {}).get("dependencies", [])
    if not isinstance(requirements, list):
        raise ValueError("project dependencies must be a list")
    direct = set()
    for requirement in requirements:
        match = re.match(rf"^({_NAME})(?=$|\s|[\[<>=!~;@])", requirement) if isinstance(requirement, str) else None
        if match is None:
            raise ValueError("invalid direct runtime dependency declaration")
        direct.add(_canonical_name(match.group(1)))

    packages = manifest.get("packages")
    if not isinstance(packages, list) or not packages:
        raise ValueError("license manifest must list packages")
    if type(manifest.get("package_count")) is not int or manifest["package_count"] != len(packages):
        raise ValueError("package_count does not match the manifest")
    package_names = set()
    notice_names = set()
    for package in packages:
        if not isinstance(package, dict) or not isinstance(package.get("name"), str) or not re.fullmatch(_NAME, package["name"]):
            raise ValueError("invalid package name in license manifest")
        name = _canonical_name(package["name"])
        if name in package_names:
            raise ValueError(f"duplicate package: {name}")
        package_names.add(name)
        if name not in pins or package.get("version") != pins[name]:
            raise ValueError(f"license package version differs from pinned dependency: {name}")
        notices = package.get("licenses")
        if not isinstance(notices, list) or not notices:
            raise ValueError(f"package has no notice files: {name}")
        for notice in notices:
            filename = notice.get("file") if isinstance(notice, dict) else None
            if not isinstance(filename, str) or not _NOTICE.fullmatch(filename):
                raise ValueError(f"notice path must be a plain .txt filename: {name}")
            key = filename.casefold()
            if key in notice_names:
                raise ValueError(f"duplicate notice file: {filename}")
            notice_names.add(key)
            path = _local_file(bundle.resolve(), bundle / filename)
            content = path.read_bytes()
            size = notice.get("size_bytes")
            if type(size) is not int or size <= 0 or size != len(content):
                raise ValueError(f"notice size does not match: {filename}")
            if _digest(notice.get("sha256"), filename) != hashlib.sha256(content).hexdigest():
                raise ValueError(f"notice SHA256 does not match: {filename}")

    missing = sorted(direct - package_names)
    if missing:
        raise ValueError(f"missing direct runtime dependency notices: {', '.join(missing)}")
    if type(manifest.get("notice_file_count")) is not int or manifest["notice_file_count"] != len(notice_names):
        raise ValueError("notice_file_count does not match the manifest")
    # The shipped directory is flat. Refuse unrecorded files of any type so
    # packaging cannot silently add notices or unrelated content.
    entries = list(bundle.iterdir())
    actual = {path.name.casefold() for path in entries}
    if len(entries) != len(actual):
        raise ValueError("notice directory contains names that collide on Windows")
    if actual != notice_names | {"manifest.json"}:
        raise ValueError("notice directory contains unregistered files or directories")
    return {
        "schema": _SCHEMA,
        "package_count": len(package_names),
        "notice_file_count": len(notice_names),
        "direct_dependency_count": len(direct),
        "constraints_sha256": constraints_hash,
        "constraints_hash_normalization": "lf",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the local dependency license bundle")
    parser.add_argument("--root", type=Path, default=_ROOT)
    args = parser.parse_args(argv)
    try:
        result = validate(args.root)
    except (OSError, ValueError) as error:
        print(f"License bundle verification failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
