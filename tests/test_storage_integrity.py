"""Mitigation M1 (risk R1/R6): a damaged data file must never be silently replaced."""

import json

import pytest
from typer.testing import CliRunner

from todo_cli import main, storage
from todo_cli.main import app
from todo_cli.storage import JsonStorage, StorageCorruptedError

TRUNCATED = (
    '[{"id": 1, "description": "pay rent", "completed": false},'
    ' {"id": 2, "description": "exam", "completed": false}'
)


def test_truncated_file_raises_instead_of_returning_empty(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text(TRUNCATED, encoding="utf-8")

    with pytest.raises(StorageCorruptedError):
        JsonStorage(path).load_tasks()


def test_add_on_truncated_file_does_not_overwrite_existing_tasks(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text(TRUNCATED, encoding="utf-8")

    with pytest.raises(StorageCorruptedError):
        JsonStorage(path).add_task("new task")

    assert path.read_text(encoding="utf-8") == TRUNCATED


@pytest.mark.parametrize(
    "content",
    ['{"tasks": []}', '[{"id": 1, "description": "x"}]', '["just a string"]'],
)
def test_valid_json_with_wrong_shape_raises(tmp_path, content):
    path = tmp_path / "tasks.json"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(StorageCorruptedError):
        JsonStorage(path).load_tasks()


def test_failed_write_keeps_previous_file_intact(tmp_path, monkeypatch):
    path = tmp_path / "tasks.json"
    store = JsonStorage(path)
    store.add_task("keep me")
    before = path.read_text(encoding="utf-8")

    def broken_dump(*args, **kwargs):
        raise OSError("disk full (simulated)")

    monkeypatch.setattr(storage.json, "dump", broken_dump)
    with pytest.raises(OSError):
        store.add_task("second")

    assert path.read_text(encoding="utf-8") == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ["tasks.json"]


def test_cli_reports_corrupted_file_and_leaves_it_untouched(tmp_path, monkeypatch):
    path = tmp_path / "tasks.json"
    path.write_text(TRUNCATED, encoding="utf-8")
    monkeypatch.setattr(main, "controller", main.TaskController.create_default(path))

    runner = CliRunner()
    for args in (["list"], ["add", "new task"], ["stats"]):
        result = runner.invoke(app, args)
        assert result.exit_code == 1, args
        assert "dañado" in result.stdout
        assert not isinstance(result.exception, json.JSONDecodeError)

    assert path.read_text(encoding="utf-8") == TRUNCATED
