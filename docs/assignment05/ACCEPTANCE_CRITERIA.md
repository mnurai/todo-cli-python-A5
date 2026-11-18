# Acceptance criteria (must remain true after every change)

| ID | Criterion | How it is verified |
|---|---|---|
| AC1 | `todo add "<text>"` stores a new task with the next ID and prints `ID: <n>`; an empty or whitespace-only description is rejected with exit code 1 and nothing is stored. | `tests/test_cli.py::test_cli_crud_flow`, `tests/test_controllers.py::test_add_task_success_and_validation` |
| AC2 | `todo complete <id>` marks the task completed; completing it again fails with exit code 1 (`TaskAlreadyCompletedError`). | `tests/test_controllers.py::test_get_and_complete_task`, CLI flow test |
| AC3 | `show`, `complete`, `update`, `remove` on a non-existent ID fail with exit code 1 and an error message, and do not change the data file. | `tests/test_controllers.py` (`TaskNotFoundError`), `tests/test_cli_errors.py` (added) |
| AC4 | Tasks persist between runs: what was saved is loaded back unchanged from the JSON file given by `TODO_CLI_PATH`. | `tests/test_storage.py::test_initialize_and_save_load`, `test_storage_find_and_replace` |
| AC5 | The full quality gate passes: `pytest -v` (0 failures) and `ruff check .` (no errors). | Command output in the evidence files |
