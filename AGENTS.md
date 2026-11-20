# AGENTS.md — instructions for AI coding agents

This file is the operating contract for any AI coding agent (Claude Code, Codex, Copilot agent, etc.)
working in this repository. Agents that do not load it automatically must be given its contents in
the prompt. Humans: read it too — it is the shortest accurate description of how this repo works.

## 1. Purpose
`todo-cli` is a small command-line task manager (add / list / show / search / complete / update /
remove / clear-completed / stats). Tasks are persisted in a single local JSON file.
It is a learning project: no network access, no accounts, no production deployment.

## 2. Architecture (layered, ~1 000 lines)
| Layer | File | Responsibility |
|---|---|---|
| Entry point / CLI | `todo_cli/main.py` | Typer commands, maps domain errors to exit codes. Console script `todo = todo_cli.main:app` |
| Business logic | `todo_cli/controllers.py` | `TaskController`, validation, domain exceptions |
| Persistence | `todo_cli/storage.py` | `TaskStorage` Protocol (the port) + `JsonStorage` (the adapter), storage-path resolution |
| Model | `todo_cli/models.py` | `Task` dataclass, (de)serialisation |
| Presentation | `todo_cli/ui.py` | Rich tables, panels, prompts |
| Tests | `tests/` | pytest: models, storage, controllers, CLI (Typer `CliRunner`) |

Dependency direction: `main → controllers → storage → models`; `main → ui → models`.
Controllers must never import Typer or Rich. UI must never touch storage.

Storage path priority: `TODO_CLI_PATH` env var → `./data/tasks.json` if it exists → `~/.todo_cli/tasks.json`.

## 3. Setup (Python ≥ 3.10)
```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[test]"
```

## 4. Safe commands (allowed without asking)
| Purpose | Command |
|---|---|
| Run all tests | `pytest -v` |
| Run one file | `pytest tests/test_storage.py -v` |
| Lint | `ruff check .` |
| Format check (no writes) | `ruff format --check .` |
| Type check | `mypy todo_cli` (install ad hoc: `pip install mypy`) |
| Build package | `python -m build` |
| Try the CLI safely | `TODO_CLI_PATH=/tmp/todo-sandbox.json todo <command>` |

Always set `TODO_CLI_PATH` to a temporary file when running the CLI by hand, so you never read or
write the user's real task list.

## 5. Coding conventions
- Python 3.10+, type hints on every public function, `from __future__ import annotations`.
- Ruff rules E, F, I, W, UP, B; line length 88. Code must pass `ruff check .` with no new ignores.
- User-facing messages are in Spanish (existing convention); code identifiers in English.
- Business rules live in `controllers.py`; raise a domain exception, never call `sys.exit` or print there.
- Keep changes small and focused: one concern per commit, imperative commit messages.

## 6. Test expectations
- Every behaviour change or bug fix comes with a test that fails before and passes after.
- Tests must use `tmp_path` / `monkeypatch` for any file I/O. Tests must never create or modify files
  in the real home directory or the repository's `data/` folder.
- `pytest -v` and `ruff check .` must both pass before a change is proposed for review.
- Never delete, skip or weaken an existing test to make a change pass; if a test encodes behaviour
  that is wrong, explain why in the PR and replace it with a test of the correct behaviour.
- Report real command output only. Never claim a test was run if it was not.

## 7. Forbidden actions (never do these)
- Read, print, create or commit secrets: `.env` files, tokens, keys, credentials, `~/.ssh`, `~/.config`.
- Read or modify the user's real data: `~/.todo_cli/`, `data/tasks.json`.
- Any deployment or publishing: `git push` to `main`, `git push --force`, PyPI upload (`twine`), releases, tags.
- Destructive commands: `rm -rf`, `git reset --hard`, `git clean -fdx`, rewriting history, deleting branches.
- Adding, removing or upgrading dependencies (`pip install <new pkg>` into pyproject, editing
  `pyproject.toml` dependencies or `requirements.txt`) without explicit human approval in the PR.
- Editing CI (`.github/workflows/`) or `AGENTS.md` itself without explicit human approval.
- Network calls from code or tests.

## 8. Review gates
1. Work on a feature branch (`agent/<short-topic>`), never directly on `main`.
2. Before asking for review: `pytest -v` and `ruff check .` pass; paste the real output.
3. Provide: summary of the change, the diff, test output, and any risk or limitation you noticed.
4. A human reviews every diff and is the only one who merges. Dependency, CI and AGENTS.md changes
   always need explicit human approval.
5. If a check fails and you cannot fix it within the task scope, stop and report — do not work around it.
