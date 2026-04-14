"""Install the versioned second-brain skills into Codex and Claude homes."""

from __future__ import annotations

import shutil
from pathlib import Path

from setup_tasks.models import SetupOptions
from setup_tasks.skill_renderer import render_skill_text
from setup_tasks.shared import REPO_ROOT, get_source_skill_path, get_target_skill_path


def copy_shared_directory(source_directory_path: Path, target_directory_path: Path) -> None:
    """Copy all entries from one shared directory into the installed skill."""
    target_directory_path.mkdir(parents=True, exist_ok=True)

    for source_entry_path in source_directory_path.iterdir():
        if source_directory_path.name == "scripts" and source_entry_path.name == "install.py":
            continue

        target_entry_path = target_directory_path / source_entry_path.name

        if source_entry_path.is_dir():
            shutil.copytree(source_entry_path, target_entry_path, dirs_exist_ok=True)
        else:
            shutil.copy2(source_entry_path, target_entry_path)


def install_skill(source_skill_path: Path, target_skill_path: Path) -> None:
    """Replace one installed skill tree with the canonical source."""
    target_skill_path.parent.mkdir(parents=True, exist_ok=True)

    if target_skill_path.exists():
        shutil.rmtree(target_skill_path)

    shutil.copytree(source_skill_path, target_skill_path)

    skill_file_path = target_skill_path / "SKILL.md"
    skill_file_path.write_text(render_skill_text(), encoding="utf-8")

    for shared_directory_name in ("scripts", "references", "init"):
        shared_directory_path = REPO_ROOT / shared_directory_name
        if shared_directory_path.is_dir():
            copy_shared_directory(
                source_directory_path=shared_directory_path,
                target_directory_path=target_skill_path / shared_directory_name,
            )


def run(options: SetupOptions) -> None:
    """Run the skill installation task for all requested homes and tools."""
    for home_path in options.home_paths:
        for tool_name in options.tool_names:
            source_skill_path = get_source_skill_path(tool_name)
            target_skill_path = get_target_skill_path(home_path, tool_name)
            install_skill(source_skill_path=source_skill_path, target_skill_path=target_skill_path)
            print(f"Installed {tool_name}:{target_skill_path}")
