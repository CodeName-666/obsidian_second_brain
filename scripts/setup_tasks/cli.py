"""CLI parsing and path resolution for the structured second-brain setup."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from setup_tasks.models import SetupOptions
from setup_tasks.shared import (
    TASK_NAMES,
    TOOL_NAMES,
    get_default_user_vault_root,
    load_base_config,
    path_exists_safely,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the setup runner."""
    argument_parser = argparse.ArgumentParser(
        description=(
            "Set up the Obsidian second brain for Codex CLI and Claude Code "
            "using structured setup tasks."
        )
    )
    argument_parser.add_argument(
        "--tool",
        choices=("all", *TOOL_NAMES),
        default="all",
        help="Install and configure Codex, Claude, or both.",
    )
    argument_parser.add_argument(
        "--home",
        action="append",
        default=[],
        help=(
            "Home directory to install into. Can be passed multiple times. "
            "When omitted, uses the current home and auto-detects one Windows "
            "home when running in WSL."
        ),
    )
    argument_parser.add_argument(
        "--vault-root",
        default="",
        help=(
            "Physical path to the Obsidian vault root. When omitted, uses "
            "OBSIDIAN_SECOND_BRAIN_ROOT or scripts/config.json."
        ),
    )
    argument_parser.add_argument(
        "--task",
        action="append",
        choices=TASK_NAMES,
        default=[],
        help=(
            "Run only selected setup tasks. Repeat the flag to run multiple "
            "tasks. When omitted, all tasks run in the default order."
        ),
    )
    return argument_parser.parse_args()


def select_names(selected_name: str, available_names: tuple[str, ...]) -> tuple[str, ...]:
    """Expand one selector into a deterministic tuple of concrete names."""
    if selected_name == "all":
        return available_names
    return (selected_name,)


def is_wsl() -> bool:
    """Detect whether the current process runs under WSL."""
    if os.name == "nt":
        return False

    try:
        with open("/proc/version", encoding="utf-8") as proc_version_file:
            return "microsoft" in proc_version_file.read().lower()
    except OSError:
        return False


def discover_wsl_windows_home() -> Path | None:
    """Try to find the Windows home directory from inside WSL."""
    windows_users_root_path = Path("/mnt/c/Users")

    if not windows_users_root_path.is_dir():
        return None

    candidate_home_paths = sorted(
        candidate_path
        for candidate_path in windows_users_root_path.iterdir()
        if candidate_path.is_dir()
        and (
            path_exists_safely(candidate_path / ".codex")
            or path_exists_safely(candidate_path / ".claude")
        )
    )

    if len(candidate_home_paths) == 1:
        return candidate_home_paths[0]

    if len(candidate_home_paths) > 1:
        preferred_home_path = windows_users_root_path / "NoName"
        if preferred_home_path.exists():
            return preferred_home_path

    return None


def resolve_home_paths(explicit_homes: list[str]) -> tuple[Path, ...]:
    """Resolve the target home directories for installation."""
    resolved_home_paths: list[Path] = []

    if len(explicit_homes) > 0:
        for home_str in explicit_homes:
            resolved_home_paths.append(Path(home_str).expanduser().resolve())
        return tuple(dict.fromkeys(resolved_home_paths))

    resolved_home_paths.append(Path.home().resolve())

    if is_wsl():
        windows_home_path = discover_wsl_windows_home()
        if windows_home_path is not None:
            resolved_home_paths.append(windows_home_path.resolve())

    return tuple(dict.fromkeys(resolved_home_paths))


def resolve_vault_root_path(explicit_vault_root: str) -> Path:
    """Resolve the physical vault root used by the setup."""
    if explicit_vault_root != "":
        return Path(explicit_vault_root).expanduser().resolve()

    environment_override = os.environ.get("OBSIDIAN_SECOND_BRAIN_ROOT", "").strip()
    if environment_override != "":
        return Path(environment_override).expanduser().resolve()

    config = load_base_config()
    platform_key = "windows" if os.name == "nt" else "posix"
    configured_root = config.get("vault_roots", {}).get(platform_key, "")

    if configured_root != "":
        return Path(configured_root).expanduser().resolve()

    return get_default_user_vault_root()


def build_options(arguments: argparse.Namespace) -> SetupOptions:
    """Normalize parsed arguments into the setup options model."""
    task_names = tuple(arguments.task) if len(arguments.task) > 0 else TASK_NAMES

    return SetupOptions(
        tool_names=select_names(arguments.tool, TOOL_NAMES),
        home_paths=resolve_home_paths(arguments.home),
        vault_root_path=resolve_vault_root_path(arguments.vault_root),
        task_names=task_names,
    )
