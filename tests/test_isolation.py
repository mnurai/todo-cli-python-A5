"""Mitigation M2 (risk R2): importing the CLI must not touch the file system."""

import os
import subprocess
import sys


def test_importing_cli_creates_no_files(tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    env = {**os.environ, "HOME": str(fake_home), "USERPROFILE": str(fake_home)}
    env.pop("TODO_CLI_PATH", None)

    subprocess.run(
        [sys.executable, "-c", "import todo_cli.main"],
        cwd=tmp_path,
        env=env,
        check=True,
    )

    assert list(fake_home.rglob("*")) == []
    assert not (tmp_path / "data").exists()
