"""Characterisation tests for CLI error handling (AC1-AC3).

Written before the Task 03 refactoring of main.py so that the refactoring can be
proven not to change user-visible behaviour (exit codes, messages, data file).
"""

import pytest
from typer.testing import CliRunner

from todo_cli import main
from todo_cli.main import app

runner = CliRunner()


@pytest.fixture
def db(tmp_path, monkeypatch):
    path = tmp_path / "tasks.json"
    monkeypatch.setenv("TODO_CLI_PATH", str(path))
    monkeypatch.setattr(main, "controller", main.TaskController.create_default(path))
    return path


@pytest.mark.parametrize(
    "args",
    [
        ["show", "99"],
        ["complete", "99"],
        ["update", "99", "new text"],
        ["remove", "99", "--yes"],
    ],
)
def test_unknown_id_fails_without_changing_data(db, args):
    runner.invoke(app, ["add", "existing task"])
    before = db.read_text(encoding="utf-8")

    result = runner.invoke(app, args)

    assert result.exit_code == 1
    assert "No existe una tarea con ID 99" in result.stdout
    assert db.read_text(encoding="utf-8") == before


def test_empty_description_is_rejected(db):
    result = runner.invoke(app, ["add", "   "])
    assert result.exit_code == 1
    assert db.read_text(encoding="utf-8").strip() == "[]"


def test_update_with_empty_description_is_rejected(db):
    runner.invoke(app, ["add", "keep me"])
    result = runner.invoke(app, ["update", "1", "   "])
    assert result.exit_code == 1
    assert "keep me" in db.read_text(encoding="utf-8")


def test_complete_twice_fails(db):
    runner.invoke(app, ["add", "once"])
    assert runner.invoke(app, ["complete", "1"]).exit_code == 0
    result = runner.invoke(app, ["complete", "1"])
    assert result.exit_code == 1
    assert "ya está completada" in result.stdout
