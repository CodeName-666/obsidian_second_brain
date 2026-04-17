"""Verify that the second-brain setup produced the required artifacts."""

from __future__ import annotations

from pathlib import Path

from setup_tasks.configure_clis import (
    MANAGED_BLOCK_END,
    MANAGED_BLOCK_START,
    get_templates_dir,
)
from setup_tasks.models import SetupOptions
from setup_tasks.shared import (
    get_expected_vault_root_strings,
    get_target_skill_path,
    load_json_file,
    load_base_config,
)


def verify_file_exists(file_path: Path, label: str) -> None:
    """Assert that one required file exists."""
    if not file_path.is_file():
        raise FileNotFoundError(f"Missing {label}: {file_path}")


def verify_directory_exists(directory_path: Path, label: str) -> None:
    """Assert that one required directory exists."""
    if not directory_path.is_dir():
        raise FileNotFoundError(f"Missing {label}: {directory_path}")


def verify_managed_block(file_path: Path, label: str) -> None:
    """Assert that one managed CLI configuration block exists."""
    verify_file_exists(file_path, label)
    file_text = file_path.read_text(encoding="utf-8")

    if MANAGED_BLOCK_START not in file_text or MANAGED_BLOCK_END not in file_text:
        raise ValueError(f"Missing managed second-brain block in {label}: {file_path}")


def verify_installed_skill(home_path: Path, tool_name: str, options: SetupOptions) -> None:
    """Verify one installed skill tree and its configured vault root."""
    target_skill_path = get_target_skill_path(home_path, tool_name)
    verify_directory_exists(target_skill_path, f"installed {tool_name} skill")
    verify_file_exists(target_skill_path / "SKILL.md", f"{tool_name} SKILL.md")
    verify_file_exists(
        target_skill_path / "scripts" / "resolve_vault_context.py",
        f"{tool_name} resolver script",
    )
    verify_file_exists(
        target_skill_path / "references" / "note-routing.md",
        f"{tool_name} note routing reference",
    )

    installed_config_path = target_skill_path / "scripts" / "config.json"
    verify_file_exists(installed_config_path, f"{tool_name} config.json")
    installed_config = load_json_file(installed_config_path)
    installed_root_strings = set(installed_config.get("vault_roots", {}).values())
    expected_root_strings = get_expected_vault_root_strings(options.vault_root_path)

    if installed_root_strings.isdisjoint(expected_root_strings):
        raise ValueError(
            f"{tool_name} config does not point to the selected vault root: {installed_config_path}"
        )


def verify_vault(options: SetupOptions) -> None:
    """Verify the created or existing vault root."""
    config = load_base_config()
    expected_directories = config.get("expected_top_level_directories", [])
    verify_directory_exists(options.vault_root_path, "vault root")
    verify_file_exists(options.vault_root_path / "README.md", "vault README.md")
    verify_file_exists(options.vault_root_path / "Brain.md", "vault Brain.md")

    for directory_name in expected_directories:
        verify_directory_exists(
            options.vault_root_path / directory_name,
            f"vault directory {directory_name}",
        )


def verify_cli_template(tool_name: str, vault_root_path: Path) -> None:
    """Verify the CLI template file stored inside the vault for one tool."""
    templates_dir = get_templates_dir(vault_root_path)
    if tool_name == "codex":
        verify_managed_block(templates_dir / "AGENTS.md", "Codex AGENTS.md template")
    if tool_name == "claude":
        verify_managed_block(templates_dir / "CLAUDE.md", "Claude CLAUDE.md template")


def run(options: SetupOptions) -> None:
    """Run all setup verification checks."""
    verify_vault(options)

    for tool_name in options.tool_names:
        verify_cli_template(tool_name=tool_name, vault_root_path=options.vault_root_path)
        print(f"Verified {tool_name} vault template")

    for home_path in options.home_paths:
        for tool_name in options.tool_names:
            verify_installed_skill(home_path=home_path, tool_name=tool_name, options=options)
            print(f"Verified {tool_name}:{home_path}")

    print(f"Verified vault:{options.vault_root_path}")
