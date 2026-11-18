"""Test isolation (AGENTS.md §6): no test may read or write the user's real data."""

import pytest

from todo_cli import main


@pytest.fixture(autouse=True)
def isolated_environment(tmp_path_factory, monkeypatch):
    sandbox = tmp_path_factory.mktemp("sandbox")
    monkeypatch.setenv("HOME", str(sandbox / "home"))
    monkeypatch.setenv("USERPROFILE", str(sandbox / "home"))
    monkeypatch.setenv("TODO_CLI_PATH", str(sandbox / "tasks.json"))
    monkeypatch.chdir(sandbox)
    monkeypatch.setattr(main, "_controller", None)
    yield
