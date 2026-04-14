"""Interactive step-by-step setup wizard for the second-brain installer."""

from __future__ import annotations

from pathlib import Path

from setup_tasks.cli import resolve_home_paths, resolve_vault_root_path, select_names
from setup_tasks.models import SetupOptions
from setup_tasks.shared import TASK_NAMES, TOOL_NAMES, get_default_user_vault_root


def prompt_text(prompt: str, default_value: str = "") -> str:
    """Prompt for one line of text with an optional default."""
    suffix = f" [{default_value}]" if default_value != "" else ""
    entered_value = input(f"{prompt}{suffix}: ").strip()

    if entered_value == "":
        return default_value

    return entered_value


def prompt_yes_no(prompt: str, default_value: bool = True) -> bool:
    """Prompt for a yes/no answer with a default."""
    suffix = "[Y/n]" if default_value else "[y/N]"
    entered_value = input(f"{prompt} {suffix}: ").strip().lower()

    if entered_value == "":
        return default_value

    return entered_value in {"y", "yes", "j", "ja"}


def prompt_tool_names() -> tuple[str, ...]:
    """Prompt for the tool selection."""
    while True:
        selected_tool = prompt_text(
            prompt="Step 1 - Installiere fuer welches Tool? (all, codex, claude)",
            default_value="all",
        ).lower()

        if selected_tool in {"all", *TOOL_NAMES}:
            return select_names(selected_tool, TOOL_NAMES)

        print("Ungueltige Auswahl. Erlaubt sind: all, codex, claude.")


def prompt_home_paths() -> tuple[Path, ...]:
    """Prompt for the target home directories."""
    while True:
        detected_home_paths = resolve_home_paths([])
        detected_home_lines = "\n".join(f"- {home_path}" for home_path in detected_home_paths)
        print("Step 2 - Erkannte Home-Verzeichnisse:")
        print(detected_home_lines)

        use_detected_homes = prompt_yes_no(
            prompt="Sollen diese Home-Verzeichnisse verwendet werden?",
            default_value=True,
        )

        if use_detected_homes:
            return detected_home_paths

        custom_home_paths: list[Path] = []
        print("Gib eigene Home-Verzeichnisse ein. Leere Eingabe beendet die Liste.")

        while True:
            custom_home = input("Home-Verzeichnis: ").strip()
            if custom_home == "":
                break
            custom_home_paths.append(Path(custom_home).expanduser().resolve())

        if len(custom_home_paths) > 0:
            return tuple(custom_home_paths)

        print("Mindestens ein Home-Verzeichnis ist erforderlich.")


def prompt_vault_root_path() -> Path:
    """Prompt for the physical vault root path."""
    default_vault_root = ""

    try:
        default_vault_root = str(resolve_vault_root_path(""))
    except FileNotFoundError:
        default_vault_root = str(get_default_user_vault_root())

    selected_vault_root = prompt_text(
        prompt="Step 3 - Wo liegt das physische Obsidian-Vault?",
        default_value=default_vault_root,
    )
    return Path(selected_vault_root).expanduser().resolve()


def confirm_summary(options: SetupOptions) -> None:
    """Show the final wizard summary before the tasks run."""
    print("\nSetup-Zusammenfassung")
    print(f"- Tools: {', '.join(options.tool_names)}")
    print(f"- Homes: {', '.join(str(home_path) for home_path in options.home_paths)}")
    print(f"- Vault: {options.vault_root_path}")
    print(f"- Aufgaben: {', '.join(options.task_names)}")

    if not prompt_yes_no("Soll das Setup jetzt gestartet werden?", default_value=True):
        raise KeyboardInterrupt("Setup aborted by user.")


def run_task_sequence(
    options: SetupOptions,
    task_runners: dict[str, object],
) -> None:
    """Run all tasks with one confirmation prompt before each step."""
    total_tasks = len(options.task_names)

    for task_index, task_name in enumerate(options.task_names, start=1):
        should_continue = prompt_yes_no(
            prompt=f"Step {task_index}/{total_tasks} - {task_name} ausfuehren?",
            default_value=True,
        )

        if not should_continue:
            raise KeyboardInterrupt(f"Setup aborted before task: {task_name}")

        print(f"[{task_index}/{total_tasks}] {task_name}")
        task_runner = task_runners[task_name]
        task_runner(options)


def run_wizard(task_runners: dict[str, object]) -> int:
    """Run the interactive step-by-step setup wizard."""
    print("Obsidian Second Brain Setup")
    print("Dieses Setup fuehrt dich Schritt fuer Schritt durch die Installation.")

    options = SetupOptions(
        tool_names=prompt_tool_names(),
        home_paths=prompt_home_paths(),
        vault_root_path=prompt_vault_root_path(),
        task_names=TASK_NAMES,
    )
    confirm_summary(options)
    run_task_sequence(options=options, task_runners=task_runners)
    return 0
