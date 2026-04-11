#!/usr/bin/env python3
"""Install the versioned Obsidian Second Brain skills into Codex and Claude homes."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

SKILL_NAME = "obsidian-second-brain"
TOOL_NAMES = ("codex", "claude")
PLATFORM_NAMES = ("wsl", "windows")
WINDOWS_USERS_ROOT_PATH = Path("/mnt/c/Users")


def path_exists_safely(candidate_path: Path) -> bool:
    """Check whether a path exists without failing on permission errors.

    Params:
        candidate_path: Path to probe for existence.

    Returns:
        `True` when the path exists and is accessible enough for the check,
        otherwise `False`.
    """
    does_exist = False

    try:
        does_exist = candidate_path.exists()
    except PermissionError:
        does_exist = False

    return does_exist


def parse_args() -> argparse.Namespace:
    """Parse installation options.

    Params:
        None.

    Returns:
        argparse.Namespace with the selected tool, platform, and optional
        Windows home override.
    """
    argument_parser = argparse.ArgumentParser(
        description="Install the versioned Obsidian Second Brain skill for Codex and Claude."
    )
    argument_parser.add_argument(
        "--tool",
        choices=("all", *TOOL_NAMES),
        default="all",
        help="Install for Codex, Claude, or both.",
    )
    argument_parser.add_argument(
        "--platform",
        choices=("all", *PLATFORM_NAMES),
        default="all",
        help="Install for WSL, Windows, or both.",
    )
    argument_parser.add_argument(
        "--windows-home",
        default="",
        help="Optional explicit Windows home path, for example /mnt/c/Users/NoName.",
    )
    arguments = argument_parser.parse_args()
    return arguments


def select_names(selected_name: str, available_names: tuple[str, ...]) -> list[str]:
    """Expand a single selector into a concrete list.

    Params:
        selected_name: The requested selector, either a specific name or `all`.
        available_names: The available concrete names.

    Returns:
        A list of resolved concrete names in deterministic order.
    """
    selected_names = list(available_names)

    if selected_name != "all":
        selected_names = [selected_name]

    return selected_names


def get_repo_root_path() -> Path:
    """Resolve the repository root that contains the versioned skills.

    Params:
        None.

    Returns:
        Absolute path to the repository root.
    """
    repo_root_path = Path(__file__).resolve().parents[1]
    return repo_root_path


def get_source_skill_path(tool_name: str) -> Path:
    """Return the versioned source directory for one tool.

    Params:
        tool_name: Target tool name, `codex` or `claude`.

    Returns:
        Absolute path to the versioned skill folder for the tool.
    """
    source_skill_path = get_repo_root_path() / tool_name / SKILL_NAME

    if not source_skill_path.is_dir():
        raise FileNotFoundError(f"Missing source skill directory: {source_skill_path}")

    return source_skill_path


def resolve_windows_home_path(explicit_windows_home: str) -> Path:
    """Resolve the Windows home directory used for Windows-target installation.

    Params:
        explicit_windows_home: Optional user-provided absolute Windows home path
            mounted in WSL notation.

    Returns:
        Absolute path to the Windows home directory.

    Raises:
        FileNotFoundError: If no suitable Windows home directory can be found.
    """
    windows_home_path = Path()

    if explicit_windows_home != "":
        windows_home_path = Path(explicit_windows_home).expanduser().resolve()

    if explicit_windows_home == "":
        if not WINDOWS_USERS_ROOT_PATH.is_dir():
            raise FileNotFoundError(
                f"Windows users root does not exist: {WINDOWS_USERS_ROOT_PATH}"
            )

        candidate_home_paths = sorted(
            candidate_path
            for candidate_path in WINDOWS_USERS_ROOT_PATH.iterdir()
            if candidate_path.is_dir()
            and (
                path_exists_safely(candidate_path / ".codex")
                or path_exists_safely(candidate_path / ".claude")
            )
        )

        if len(candidate_home_paths) == 1:
            windows_home_path = candidate_home_paths[0]

        if len(candidate_home_paths) > 1:
            preferred_home_path = WINDOWS_USERS_ROOT_PATH / "NoName"

            if preferred_home_path.exists():
                windows_home_path = preferred_home_path

    if windows_home_path == Path():
        raise FileNotFoundError(
            "Could not resolve the Windows home path. Pass --windows-home explicitly."
        )

    return windows_home_path


def get_target_skill_path(tool_name: str, platform_name: str, windows_home_path: Path) -> Path:
    """Build the installation target path for one tool and platform.

    Params:
        tool_name: Target tool name, `codex` or `claude`.
        platform_name: Target platform name, `wsl` or `windows`.
        windows_home_path: Resolved Windows home path for Windows targets.

    Returns:
        Absolute target path where the skill should be installed.
    """
    target_skill_path = Path()

    if platform_name == "wsl":
        target_skill_path = Path.home() / f".{tool_name}" / "skills" / SKILL_NAME

    if platform_name == "windows":
        target_skill_path = windows_home_path / f".{tool_name}" / "skills" / SKILL_NAME

    return target_skill_path


def install_skill(source_skill_path: Path, target_skill_path: Path) -> None:
    """Replace one installed skill directory with the versioned source.

    Params:
        source_skill_path: Canonical source directory from the versioned repo.
        target_skill_path: Destination directory in the local tool home.

    Returns:
        None. The function copies the full skill tree into place.
    """
    target_parent_path = target_skill_path.parent
    target_parent_path.mkdir(parents=True, exist_ok=True)

    if target_skill_path.exists():
        shutil.rmtree(target_skill_path)

    shutil.copytree(source_skill_path, target_skill_path)


def main() -> int:
    """Install the selected skill variants into the selected targets.

    Params:
        None.

    Returns:
        Process exit code. `0` indicates success.
    """
    arguments = parse_args()
    selected_tool_names = select_names(arguments.tool, TOOL_NAMES)
    selected_platform_names = select_names(arguments.platform, PLATFORM_NAMES)
    windows_home_path = Path()

    if "windows" in selected_platform_names:
        windows_home_path = resolve_windows_home_path(arguments.windows_home)

    for tool_name in selected_tool_names:
        source_skill_path = get_source_skill_path(tool_name)

        for platform_name in selected_platform_names:
            target_skill_path = get_target_skill_path(
                tool_name=tool_name,
                platform_name=platform_name,
                windows_home_path=windows_home_path,
            )
            install_skill(source_skill_path=source_skill_path, target_skill_path=target_skill_path)
            print(f"Installed {tool_name}:{SKILL_NAME} -> {target_skill_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
