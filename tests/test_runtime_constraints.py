from pathlib import Path

import pytest

from scripts.verify_runtime_constraints import validate


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
