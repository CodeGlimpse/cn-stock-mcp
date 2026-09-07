import copy
import hashlib
import json
from pathlib import Path

import pytest

from scripts.verify_license_bundle import main, validate


def _write_manifest(root, manifest):
    (root / "third_party_licenses" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


@pytest.fixture
def bundle(tmp_path):
    root = tmp_path / "share" / "cn-stock-mcp"
    notices = root / "third_party_licenses"
    notices.mkdir(parents=True)
    constraints = b"# Versioned runtime\nroot_package==1.0\naddon==2.0\n"
    (root / "constraints-windows-py313.txt").write_bytes(constraints)
    (root / "pyproject.toml").write_text(
        '[project]\ndependencies = ["Root.Package[cli]>=1.0"]\n', encoding="utf-8"
    )
    manifest = {
        "schema": "cn_stock_third_party_licenses_v1",
        "constraints_hash_normalization": "lf",
        "constraints_sha256": hashlib.sha256(constraints).hexdigest(),
        "package_count": 2,
        "notice_file_count": 2,
        "packages": [],
    }
    for name, version in (("root-package", "1.0"), ("addon", "2.0")):
        content = f"Copyright {name}\r\nPermission notice\r\n".encode()
        filename = f"{name}-{version}-LICENSE.txt"
        (notices / filename).write_bytes(content)
        manifest["packages"].append({
            "name": name,
            "version": version,
            "licenses": [{"file": filename, "size_bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}],
        })
    _write_manifest(root, manifest)
    return root, manifest


def test_valid_bundle_works_from_installed_share_layout(bundle, capsys):
    root, _manifest = bundle
    result = validate(root)
    assert result["package_count"] == 2
    assert result["notice_file_count"] == 2
    assert result["direct_dependency_count"] == 1
    assert main(["--root", str(root)]) == 0
    assert json.loads(capsys.readouterr().out) == result


@pytest.mark.parametrize("newline", [b"\n", b"\r\n", b"\r"])
def test_constraints_hash_is_stable_across_checkout_line_endings(bundle, newline):
    root, manifest = bundle
    path = root / "constraints-windows-py313.txt"
    path.write_bytes(path.read_bytes().replace(b"\n", newline))
    assert validate(root)["constraints_sha256"] == manifest["constraints_sha256"]


def test_notice_bytes_are_not_line_ending_normalized(bundle):
    root, manifest = bundle
    notice = manifest["packages"][0]["licenses"][0]
    path = root / "third_party_licenses" / notice["file"]
    path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
    with pytest.raises(ValueError, match="notice size does not match"):
        validate(root)


def test_same_size_corruption_is_detected_by_hash(bundle):
    root, manifest = bundle
    path = root / "third_party_licenses" / manifest["packages"][0]["licenses"][0]["file"]
    content = path.read_bytes()
    path.write_bytes(b"!" + content[1:])
    with pytest.raises(ValueError, match="notice SHA256 does not match"):
        validate(root)


def test_absent_notice_is_rejected(bundle):
    root, manifest = bundle
    (root / "third_party_licenses" / manifest["packages"][0]["licenses"][0]["file"]).unlink()
    with pytest.raises(ValueError, match="missing bundle file"):
        validate(root)


def test_missing_direct_dependency_is_detected_even_when_counts_are_updated(bundle):
    root, manifest = bundle
    manifest["packages"].pop(0)
    manifest["package_count"] = manifest["notice_file_count"] = 1
    _write_manifest(root, manifest)
    with pytest.raises(ValueError, match="missing direct runtime dependency notices: root-package"):
        validate(root)


def test_manifest_version_must_match_the_pinned_dependency(bundle):
    root, manifest = bundle
    manifest["packages"][0]["version"] = "1.1"
    _write_manifest(root, manifest)
    with pytest.raises(ValueError, match="version differs from pinned dependency"):
        validate(root)


def test_constraint_changes_invalidate_the_review_hash(bundle):
    root, _manifest = bundle
    path = root / "constraints-windows-py313.txt"
    path.write_bytes(path.read_bytes().replace(b"addon==2.0", b"addon==2.1"))
    with pytest.raises(ValueError, match="constraints SHA256 does not match"):
        validate(root)


def test_duplicate_constraint_names_are_rejected(bundle):
    root, manifest = bundle
    path = root / "constraints-windows-py313.txt"
    constraints = path.read_bytes() + b"Root.Package==1.0\n"
    path.write_bytes(constraints)
    manifest["constraints_sha256"] = hashlib.sha256(constraints).hexdigest()
    _write_manifest(root, manifest)
    with pytest.raises(ValueError, match="duplicate constraint: root-package"):
        validate(root)


def test_a_package_requires_at_least_one_original_notice(bundle):
    root, manifest = bundle
    manifest["packages"][0]["licenses"] = []
    _write_manifest(root, manifest)
    with pytest.raises(ValueError, match="package has no notice files"):
        validate(root)


def test_package_name_duplicates_use_normalized_names(bundle):
    root, manifest = bundle
    duplicate = copy.deepcopy(manifest["packages"][0])
    duplicate["name"] = "Root_Package"
    manifest["packages"].append(duplicate)
    manifest["package_count"] += 1
    manifest["notice_file_count"] += 1
    _write_manifest(root, manifest)
    with pytest.raises(ValueError, match="duplicate package: root-package"):
        validate(root)


def test_notice_cannot_be_registered_twice(bundle):
    root, manifest = bundle
    manifest["packages"][1]["licenses"] = copy.deepcopy(manifest["packages"][0]["licenses"])
    _write_manifest(root, manifest)
    with pytest.raises(ValueError, match="duplicate notice file"):
        validate(root)


@pytest.mark.parametrize("field", ["package_count", "notice_file_count"])
def test_manifest_counts_must_match_registered_evidence(bundle, field):
    root, manifest = bundle
    manifest[field] += 1
    _write_manifest(root, manifest)
    with pytest.raises(ValueError, match=field):
        validate(root)


@pytest.mark.parametrize("filename", ["../outside.txt", "..\\outside.txt", "/outside.txt", "C:\\outside.txt", "notice.txt:stream.txt"])
def test_notice_paths_cannot_escape_the_bundle(bundle, filename):
    root, manifest = bundle
    manifest["packages"][0]["licenses"][0]["file"] = filename
    _write_manifest(root, manifest)
    with pytest.raises(ValueError, match="plain .txt filename"):
        validate(root)


def test_resolved_notice_path_cannot_escape_through_a_link(bundle, monkeypatch):
    root, manifest = bundle
    target = root / "third_party_licenses" / manifest["packages"][0]["licenses"][0]["file"]
    original_resolve = Path.resolve

    def resolve(path, *args, **kwargs):
        if path == target:
            return root.parent / "outside.txt"
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve)
    with pytest.raises(ValueError, match="escapes bundle root"):
        validate(root)


def test_extra_unregistered_text_file_is_rejected(bundle):
    root, _manifest = bundle
    (root / "third_party_licenses" / "UNREVIEWED.txt").write_bytes(b"Unregistered notice")
    with pytest.raises(ValueError, match="unregistered files"):
        validate(root)


def test_cli_reports_missing_bundle_as_failure(tmp_path, capsys):
    assert main(["--root", str(tmp_path)]) == 1
    output = capsys.readouterr()
    assert output.out == ""
    assert "License bundle verification failed: missing bundle file" in output.err
