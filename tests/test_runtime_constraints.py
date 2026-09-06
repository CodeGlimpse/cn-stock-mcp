from pathlib import Path
from importlib import metadata
from types import SimpleNamespace

import pytest

from scripts.verify_runtime_constraints import validate, verify_installed_runtime


def test_windows_runtime_constraints_cover_direct_dependencies():
    names = validate(Path(__file__).parents[1] / "constraints-windows-py313.txt")

    assert {"akshare", "cachetools", "mcp", "pydantic-settings"}.issubset(names)


def test_runtime_constraints_reject_unpinned_or_duplicate_entries(tmp_path: Path):
    path = tmp_path / "constraints.txt"
    path.write_text(
        "\n".join(
            [
                "akshare==1.0",
                "akshare==1.1",
                "cachetools>=5",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate constraint|expected an exact"):
        validate(path)


def _runtime_fixture(tmp_path, pins, packages, requirements='"root[cli]>=1"'):
    project = tmp_path / "pyproject.toml"
    project.write_text(f"[project]\ndependencies = [{requirements}]\n", encoding="utf-8")
    constraints = tmp_path / "constraints.txt"
    constraints.write_text("\n".join(pins), encoding="utf-8")

    def lookup(name):
        if name not in packages:
            raise metadata.PackageNotFoundError(name)
        version, requires = packages[name]
        return SimpleNamespace(version=version, requires=requires)

    return constraints, project, lookup


def test_runtime_check_finds_unpinned_transitive_dependency(tmp_path):
    constraints, project, lookup = _runtime_fixture(
        tmp_path,
        ["root==1", "curl-cffi==1"],
        {"root": ("1", ["curl_cffi>=1"]), "curl-cffi": ("1", ["cffi>=2"]), "cffi": ("2.1.1", [])},
    )
    with pytest.raises(ValueError, match="unconstrained runtime dependency: cffi"):
        verify_installed_runtime(constraints, project, distribution=lookup)


def test_runtime_check_traverses_extras_markers_and_cycles(tmp_path):
    constraints, project, lookup = _runtime_fixture(
        tmp_path,
        ["root==1", "cli-addon==2", "windows-addon==3"],
        {
            "root": ("1", ['cli-addon>=2; extra == "cli"', 'unix-addon; sys_platform == "linux"']),
            "cli-addon": ("2", ['windows-addon; sys_platform == "win32"', "root[cli]>=1"]),
            "windows-addon": ("3", []),
        },
    )
    assert verify_installed_runtime(
        constraints, project, distribution=lookup, environment={"sys_platform": "win32"}
    ) == ["cli-addon", "root", "windows-addon"]


def test_runtime_check_revisits_dependency_when_new_extra_is_requested(tmp_path):
    constraints, project, lookup = _runtime_fixture(
        tmp_path,
        ["root==1", "feature==1", "addon==1"],
        {
            "root": ("1", ["feature", "feature[optional]"]),
            "feature": ("1", ['addon; extra == "optional"']),
            "addon": ("1", []),
        },
    )
    assert verify_installed_runtime(constraints, project, distribution=lookup) == ["addon", "feature", "root"]


@pytest.mark.parametrize(
    ("pins", "packages", "error"),
    [
        (["root==1", "addon==2"], {"root": ("1", ["addon>=1"]), "addon": ("1", [])}, "differs from pinned"),
        (["root==1", "addon==1"], {"root": ("1", ["addon>=2"]), "addon": ("1", [])}, "does not satisfy"),
        (["root==1", "addon==1"], {"root": ("1", ["addon>=1"])}, "not installed: addon"),
    ],
)
def test_runtime_check_rejects_inconsistent_installed_environment(tmp_path, pins, packages, error):
    constraints, project, lookup = _runtime_fixture(tmp_path, pins, packages)
    with pytest.raises(ValueError, match=error):
        verify_installed_runtime(constraints, project, distribution=lookup)


def test_direct_dependency_check_reads_project_declarations(tmp_path):
    constraints, project, _lookup = _runtime_fixture(tmp_path, ["old==1"], {}, requirements='"new-package>=1"')
    with pytest.raises(ValueError, match="missing direct runtime dependency: new-package"):
        validate(constraints, project)
