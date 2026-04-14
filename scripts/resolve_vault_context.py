#!/usr/bin/env python3
"""Resolve the active Obsidian second-brain vault and report structure drift."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.json"


def load_config() -> dict:
    """Load the skill configuration from the JSON file next to this script.

    Returns:
        Parsed configuration dictionary. Falls back to empty defaults when
        the file is missing.
    """
    if CONFIG_PATH.is_file():
        with open(CONFIG_PATH, encoding="utf-8") as config_file:
            return json.load(config_file)
    return {}


def get_config_value(config: dict, key: str, default: object = None) -> object:
    """Read a single value from the loaded config with a fallback.

    Params:
        config: Parsed config dictionary.
        key: Top-level key to look up.
        default: Value returned when the key is absent.

    Returns:
        The config value or the provided default.
    """
    return config.get(key, default)


_CONFIG = load_config()

EXPECTED_TOP_LEVEL_DIRECTORIES = tuple(
    get_config_value(_CONFIG, "expected_top_level_directories", [
        "00 Kontext",
        "01 Inbox",
        "02 Projekte",
        "03 Bereiche",
        "04 Ressourcen",
        "05 Daily Notes",
        "06 Archive",
        "07 Anhänge",
    ])
)
MOUNT_NAMES = tuple(
    get_config_value(_CONFIG, "mount_names", ["obsidian", ".obsidian"])
)


def get_default_vault_roots() -> tuple[Path, ...]:
    """Return platform-aware default vault roots, preferring explicit overrides."""
    environment_override = os.environ.get("OBSIDIAN_SECOND_BRAIN_ROOT", "").strip()
    default_vault_roots: list[Path] = []

    if environment_override != "":
        default_vault_roots.append(Path(environment_override).expanduser())

    vault_roots_config = get_config_value(_CONFIG, "vault_roots", {})
    platform_key = "windows" if os.name == "nt" else "posix"
    configured_root = vault_roots_config.get(platform_key, "")

    if configured_root != "":
        default_vault_roots.append(Path(configured_root).expanduser())

    default_vault_roots.append(Path.home().resolve() / ".obsidian_brain")

    return tuple(default_vault_roots)


def is_vault_root(candidate_path: Path) -> bool:
    """Return whether the candidate path looks like the vault root."""
    brain_file_path = candidate_path / "Brain.md"
    is_vault = candidate_path.is_dir() and brain_file_path.is_file()
    return is_vault


def iter_candidate_paths(start_path: Path) -> Iterable[tuple[str, Path]]:
    """Yield vault candidates from local context first, then the stable fallback path."""
    resolved_start_path = start_path.resolve()

    if is_vault_root(resolved_start_path):
        yield ("cwd", resolved_start_path)

    for parent_path in (resolved_start_path, *resolved_start_path.parents):
        for mount_name in MOUNT_NAMES:
            yield (f"mount:{mount_name}", parent_path / mount_name)

    for default_vault_root in get_default_vault_roots():
        yield ("default", default_vault_root)


def resolve_vault_root(start_path: Path) -> tuple[str, Path]:
    """Resolve the first matching vault root and report where it came from."""
    seen_real_paths: set[Path] = set()
    chosen_source = ""
    chosen_path = Path()

    for source_name, candidate_path in iter_candidate_paths(start_path):
        real_candidate_path = candidate_path.resolve(strict=False)
        should_check_candidate = real_candidate_path not in seen_real_paths

        if should_check_candidate:
            seen_real_paths.add(real_candidate_path)

            if is_vault_root(real_candidate_path):
                chosen_source = source_name
                chosen_path = real_candidate_path
                break

    if chosen_source == "":
        raise FileNotFoundError(
            "Could not resolve the Obsidian vault root. Checked the default path "
            "and parent directories for obsidian/.obsidian mounts containing Brain.md."
        )

    return chosen_source, chosen_path


def collect_top_level_entries(vault_root_path: Path) -> list[str]:
    """List top-level vault entries except the Git metadata directory."""
    entry_names = sorted(
        entry_path.name for entry_path in vault_root_path.iterdir() if entry_path.name != ".git"
    )
    return entry_names


def build_report(start_path: Path) -> dict[str, object]:
    """Build a JSON-serializable context report for the resolved vault."""
    source_name, vault_root_path = resolve_vault_root(start_path)
    top_level_entries = collect_top_level_entries(vault_root_path)
    present_expected_directories = [
        directory_name
        for directory_name in EXPECTED_TOP_LEVEL_DIRECTORIES
        if (vault_root_path / directory_name).is_dir()
    ]
    missing_expected_directories = [
        directory_name
        for directory_name in EXPECTED_TOP_LEVEL_DIRECTORIES
        if directory_name not in present_expected_directories
    ]

    report = {
        "cwd": str(start_path.resolve()),
        "vault_root": str(vault_root_path),
        "brain_md": str(vault_root_path / "Brain.md"),
        "resolved_from": source_name,
        "top_level_entries": top_level_entries,
        "expected_top_level_directories": list(EXPECTED_TOP_LEVEL_DIRECTORIES),
        "present_expected_directories": present_expected_directories,
        "missing_expected_directories": missing_expected_directories,
    }
    return report


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for vault resolution."""
    argument_parser = argparse.ArgumentParser(
        description="Resolve the Obsidian second-brain vault and print JSON context."
    )
    argument_parser.add_argument(
        "--cwd",
        default=".",
        help="Working directory used to search for mounted vault paths.",
    )
    return argument_parser.parse_args()


def main() -> int:
    """Resolve the vault and print the report."""
    arguments = parse_args()
    start_path = Path(arguments.cwd).expanduser()
    report = build_report(start_path)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
