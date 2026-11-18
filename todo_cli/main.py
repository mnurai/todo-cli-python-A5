from __future__ import annotations

import functools
from collections.abc import Callable
from typing import ParamSpec, TypeVar

import typer
from rich.console import Console

from todo_cli.controllers import (
    InvalidTaskDescriptionError,
    TaskAlreadyCompletedError,
    TaskController,
    TaskNotFoundError,
)
from todo_cli.ui import TaskUI

app = typer.Typer(
    name="todo",
    help="Aplicación CLI para la gestión de tareas.",
    add_completion=False,
)

console = Console()
controller = TaskController.create_default()
ui = TaskUI()


P = ParamSpec("P")
R = TypeVar("R")

DOMAIN_ERRORS = (
    InvalidTaskDescriptionError,
    TaskAlreadyCompletedError,
    TaskNotFoundError,
)


def handle_domain_errors(command: Callable[P, R]) -> Callable[P, R]:
    """
    Traduce las excepciones de dominio en un mensaje de error y código de salida 1.

    Centraliza el bloque try/except que antes se repetía en cada comando.
    """

    @functools.wraps(command)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return command(*args, **kwargs)
        except DOMAIN_ERRORS as error:
            ui.show_error(str(error))
            raise typer.Exit(code=1) from error

    return wrapper


@app.command("add")
@handle_domain_errors
def add_task(description: str) -> None:
    """
    Agrega una nueva tarea.
    """
    task = controller.add_task(description)

    ui.show_success(
        f"Tarea agregada correctamente.\n\n"
        f"ID: {task.id}\n"
        f"Descripción: {task.description}"
    )


@app.command("list")
def list_tasks() -> None:
    """
    Lista todas las tareas.
    """
    tasks = controller.list_tasks()

    ui.show_tasks(tasks)
    ui.show_statistics(
        total=controller.task_count(),
        pending=controller.pending_count(),
        completed=controller.completed_count(),
    )


@app.command("complete")
@handle_domain_errors
def complete_task(task_id: int) -> None:
    """
    Marca una tarea como completada.
    """
    task = controller.complete_task(task_id)

    ui.show_success(
        f"La tarea #{task.id} fue marcada como completada."
    )


@app.command("remove")
@handle_domain_errors
def remove_task(
    task_id: int,
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Confirma la eliminación sin solicitar confirmación interactiva.",
    ),
) -> None:
    """
    Elimina una tarea.
    """
    task = controller.get_task(task_id)

    if not yes and not ui.confirm(
        f"¿Desea eliminar la tarea #{task.id}?"
    ):
        ui.show_warning("Operación cancelada.")
        return

    controller.delete_task(task_id)

    ui.show_success(
        f"La tarea #{task_id} fue eliminada."
    )


@app.command("show")
@handle_domain_errors
def show_task(task_id: int) -> None:
    """
    Muestra una tarea específica.
    """
    task = controller.get_task(task_id)
    ui.show_task(task)


@app.command("pending")
def pending_tasks() -> None:
    """
    Lista únicamente las tareas pendientes.
    """
    tasks = controller.pending_tasks()

    ui.show_tasks(tasks)

    ui.show_statistics(
        total=len(tasks),
        pending=len(tasks),
        completed=0,
    )


@app.command("completed")
def completed_tasks() -> None:
    """
    Lista únicamente las tareas completadas.
    """
    tasks = controller.completed_tasks()

    ui.show_tasks(tasks)

    ui.show_statistics(
        total=len(tasks),
        pending=0,
        completed=len(tasks),
    )


@app.command("update")
@handle_domain_errors
def update_task(
    task_id: int,
    description: str,
) -> None:
    """
    Actualiza la descripción de una tarea.
    """
    task = controller.update_description(
        task_id,
        description,
    )

    ui.show_success(
        f"La tarea #{task.id} fue actualizada."
    )


@app.command("search")
def search_tasks(query: str) -> None:
    """
    Busca tareas por coincidencia de texto en la descripción.
    """
    tasks = controller.search_tasks(query)

    if not tasks:
        ui.show_warning(
            f"No se encontraron tareas que contengan '{query}'."
        )
        return

    ui.show_tasks(tasks)
    ui.show_statistics(
        total=len(tasks),
        pending=sum(1 for t in tasks if not t.completed),
        completed=sum(1 for t in tasks if t.completed),
    )


@app.command("clear-completed")
def clear_completed(
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Confirma la eliminación sin solicitar confirmación interactiva.",
    ),
) -> None:
    """
    Elimina todas las tareas completadas.
    """
    if controller.completed_count() == 0:
        ui.show_warning(
            "No existen tareas completadas."
        )
        return

    if not yes and not ui.confirm(
        f"¿Desea eliminar las {controller.completed_count()} tareas completadas?"
    ):
        ui.show_warning("Operación cancelada.")
        return

    removed = controller.clear_completed_tasks()

    ui.show_success(
        f"Se eliminaron {removed} tarea(s) completada(s)."
    )


@app.command("stats")
def statistics() -> None:
    """
    Muestra estadísticas generales.
    """
    ui.show_statistics(
        total=controller.task_count(),
        pending=controller.pending_count(),
        completed=controller.completed_count(),
    )


@app.command("version")
def version() -> None:
    """
    Muestra la versión de la aplicación.
    """
    console.print(
        "[bold green]To-Do CLI[/bold green] v1.1.0"
    )


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """
    Punto de entrada principal.
    """
    if ctx.invoked_subcommand is None:
        ui.print_header()
        console.print()
        console.print(
            "[bold cyan]Comandos disponibles:[/bold cyan]"
        )
        console.print("  add")
        console.print("  list")
        console.print("  show")
        console.print("  search")
        console.print("  complete")
        console.print("  remove")
        console.print("  update")
        console.print("  pending")
        console.print("  completed")
        console.print("  clear-completed")
        console.print("  stats")
        console.print("  version")
        console.print()
        console.print(
            "Ejecute [bold]todo --help[/bold] para más información."
        )


if __name__ == "__main__":
    app()
