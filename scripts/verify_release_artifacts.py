"""Compare release files with published hashes before any upload.

The local check and comparison functions never access the network. The CLI
only reads public release metadata unless --local-only is selected. In CI,
GH_TOKEN is used solely as a GitHub API request header and is never logged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def local_manifest(version: str, root: Path) -> dict[str, str]:
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:(?:a|b|rc)\d+|\.post\d+|\.dev\d+)?", version):
        raise ValueError("unsupported release version")
    package_names = {
        f"cn_stock_mcp-{version}-py3-none-any.whl",
        f"cn_stock_mcp-{version}.tar.gz",
    }
    actual_names = {path.name for path in (root / "dist").iterdir() if path.is_file()}
    if actual_names != package_names:
        raise ValueError("dist must contain exactly the wheel and sdist for this version")
    files = {name: root / "dist" / name for name in package_names}
    for name in ("constraints-windows-py313.txt", "sbom.json", "sha256sums.txt"):
        files[name] = root / name
    hashes = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in files.items()}
    recorded = {}
    for line in files["sha256sums.txt"].read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-fA-F]{64})\s+\*?([A-Za-z0-9][A-Za-z0-9_.+-]*)", line)
        if not match or match.group(2) in recorded:
            raise ValueError("checksum manifest contains an invalid or duplicate entry")
        recorded[match.group(2)] = match.group(1).lower()
    expected = {name: value for name, value in hashes.items() if name != "sha256sums.txt"}
    if recorded != expected:
        raise ValueError("checksum manifest does not match the release files")
    return hashes


def _check_files(expected: dict[str, str], actual: dict[str, str], source: str, complete: bool) -> list[str]:
    if actual.keys() - expected.keys():
        raise ValueError(f"{source} contains unexpected files for this release")
    for name, digest in actual.items():
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
            raise ValueError(f"{source} has no usable SHA256 for {name}")
        if expected[name] != digest.lower():
            raise ValueError(f"{source} already contains different bytes for {name}; reuse the original artifact or publish a new version")
    missing = sorted(expected.keys() - actual.keys())
    if complete and missing:
        raise ValueError(f"{source} release is incomplete: {', '.join(missing)}")
    return missing


def compare_releases(
    manifest: dict[str, str],
    version: str,
    pypi: dict | None,
    github: dict | None,
    *,
    require_complete: bool = False,
) -> dict:
    packages = {name: digest for name, digest in manifest.items() if name.endswith((".whl", ".tar.gz"))}
    pypi_files = {}
    if pypi is not None:
        if pypi.get("info", {}).get("version") != version:
            raise ValueError("PyPI metadata returned a different version")
        for item in pypi.get("urls", []):
            name = item.get("filename")
            if not isinstance(name, str) or name in pypi_files:
                raise ValueError("PyPI metadata contains an invalid or duplicate filename")
            pypi_files[name] = item.get("digests", {}).get("sha256")
    github_files = {}
    if github is not None:
        if github.get("tag_name") != f"v{version}" or github.get("draft"):
            raise ValueError("GitHub release tag or publication state does not match")
        for item in github.get("assets", []):
            name = item.get("name")
            if not isinstance(name, str) or name in github_files:
                raise ValueError("GitHub metadata contains an invalid or duplicate filename")
            digest = item.get("digest")
            github_files[name] = digest.removeprefix("sha256:") if isinstance(digest, str) and digest.startswith("sha256:") else None
    return {
        "version": version,
        "github_release_exists": github is not None,
        "pypi_missing_files": _check_files(packages, pypi_files, "PyPI", require_complete),
        "github_missing_files": _check_files(manifest, github_files, "GitHub", require_complete),
    }


def _read_metadata(url: str, source: str, headers: dict[str, str] | None = None) -> dict | None:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "cn-stock-mcp-release-check", **(headers or {})})
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except HTTPError as error:
        if error.code == 404:
            return None
        raise ValueError(f"{source} metadata request failed with HTTP {error.code}") from None
    except (URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError(f"{source} metadata could not be verified") from None
    if not isinstance(payload, dict):
        raise ValueError(f"{source} returned invalid release metadata")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify immutable PyPI/GitHub release artifacts")
    parser.add_argument("--version", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--repository")
    parser.add_argument("--local-only", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    try:
        manifest = local_manifest(args.version, args.root)
        if args.local_only:
            result = {"version": args.version, "files": manifest}
        else:
            if not args.repository or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repository):
                raise ValueError("--repository must be an owner/repository name")
            pypi = _read_metadata(f"https://pypi.org/pypi/cn-stock-mcp/{args.version}/json", "PyPI")
            headers = {"Authorization": f"Bearer {os.environ['GH_TOKEN']}"} if os.environ.get("GH_TOKEN") else {}
            github = _read_metadata(
                f"https://api.github.com/repos/{args.repository}/releases/tags/v{args.version}",
                "GitHub", headers,
            )
            result = compare_releases(manifest, args.version, pypi, github, require_complete=args.require_complete)
    except (OSError, ValueError) as error:
        print(f"Release verification failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
