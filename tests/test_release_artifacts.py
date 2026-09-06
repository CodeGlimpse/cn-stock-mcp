import hashlib
from urllib.error import HTTPError, URLError

import pytest

from scripts.verify_release_artifacts import _read_metadata, compare_releases, local_manifest


VERSION = "0.2.3"
WHEEL = f"cn_stock_mcp-{VERSION}-py3-none-any.whl"
SDIST = f"cn_stock_mcp-{VERSION}.tar.gz"


@pytest.fixture
def release_files(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    files = {WHEEL: dist / WHEEL, SDIST: dist / SDIST}
    files.update({name: tmp_path / name for name in ("constraints-windows-py313.txt", "sbom.json")})
    for name, path in files.items():
        path.write_bytes(f"test release file: {name}".encode())
    checksums = "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {name}\n" for name, path in files.items())
    (tmp_path / "sha256sums.txt").write_text(checksums, encoding="utf-8")
    return tmp_path, local_manifest(VERSION, tmp_path)


def _remote(manifest):
    pypi = {
        "info": {"version": VERSION},
        "urls": [{"filename": name, "digests": {"sha256": manifest[name]}} for name in (WHEEL, SDIST)],
    }
    github = {
        "tag_name": f"v{VERSION}", "draft": False,
        "assets": [{"name": name, "digest": f"sha256:{digest}"} for name, digest in manifest.items()],
    }
    return pypi, github


def test_first_release_reports_only_missing_files(release_files):
    _root, manifest = release_files
    result = compare_releases(manifest, VERSION, None, None)
    assert result["github_release_exists"] is False
    assert set(result["pypi_missing_files"]) == {WHEEL, SDIST}
    assert set(result["github_missing_files"]) == set(manifest)


def test_identical_release_can_be_rechecked_without_upload(release_files):
    _root, manifest = release_files
    result = compare_releases(manifest, VERSION, *_remote(manifest), require_complete=True)
    assert result["github_release_exists"] is True
    assert result["pypi_missing_files"] == result["github_missing_files"] == []


@pytest.mark.parametrize("source", ["PyPI", "GitHub"])
def test_rerun_rejects_same_filename_with_different_bytes(release_files, source):
    _root, manifest = release_files
    pypi, github = _remote(manifest)
    if source == "PyPI":
        pypi["urls"][0]["digests"]["sha256"] = "0" * 64
    else:
        github["assets"][0]["digest"] = "sha256:" + "0" * 64
    with pytest.raises(ValueError, match=f"{source} already contains different bytes"):
        compare_releases(manifest, VERSION, pypi, github)


def test_interrupted_upload_may_add_missing_files_but_is_not_complete(release_files):
    _root, manifest = release_files
    pypi, github = _remote(manifest)
    github["assets"] = [item for item in github["assets"] if item["name"] != "sbom.json"]
    result = compare_releases(manifest, VERSION, pypi, github)
    assert result["github_missing_files"] == ["sbom.json"]
    with pytest.raises(ValueError, match="GitHub release is incomplete"):
        compare_releases(manifest, VERSION, pypi, github, require_complete=True)


def test_absent_release_is_not_a_successful_post_publish_check(release_files):
    with pytest.raises(ValueError, match="release is incomplete"):
        compare_releases(release_files[1], VERSION, None, None, require_complete=True)


def test_missing_remote_digest_requires_verification(release_files):
    _root, manifest = release_files
    pypi, github = _remote(manifest)
    github["assets"][0]["digest"] = None
    with pytest.raises(ValueError, match="no usable SHA256"):
        compare_releases(manifest, VERSION, pypi, github)


def test_local_modified_artifact_is_rejected(release_files):
    root, _manifest = release_files
    (root / "dist" / WHEEL).write_bytes(b"changed after checksumming")
    with pytest.raises(ValueError, match="checksum manifest does not match"):
        local_manifest(VERSION, root)


def test_stale_distribution_is_rejected(release_files):
    root, _manifest = release_files
    (root / "dist" / "old-version.whl").write_bytes(b"old")
    with pytest.raises(ValueError, match="exactly the wheel and sdist"):
        local_manifest(VERSION, root)


@pytest.mark.parametrize("code", [401, 403, 429, 500])
def test_api_errors_are_not_treated_as_an_absent_release(monkeypatch, code):
    def fail(*args, **kwargs):
        raise HTTPError("https://example.test", code, "error", {}, None)
    monkeypatch.setattr("scripts.verify_release_artifacts.urlopen", fail)
    with pytest.raises(ValueError, match=f"HTTP {code}"):
        _read_metadata("https://example.test", "GitHub")


def test_only_404_is_treated_as_an_absent_release(monkeypatch):
    def fail(*args, **kwargs):
        raise HTTPError("https://example.test", 404, "not found", {}, None)
    monkeypatch.setattr("scripts.verify_release_artifacts.urlopen", fail)
    assert _read_metadata("https://example.test", "GitHub") is None


def test_network_failure_is_not_an_absent_release(monkeypatch):
    def fail(*args, **kwargs):
        raise URLError("offline")
    monkeypatch.setattr("scripts.verify_release_artifacts.urlopen", fail)
    with pytest.raises(ValueError, match="could not be verified"):
        _read_metadata("https://example.test", "GitHub")
