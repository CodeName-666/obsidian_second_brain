"""Shared constants and helpers for the second-brain setup tasks."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path, PurePosixPath, PureWindowsPath

SKILL_NAME = "obsidian-second-brain"
TOOL_NAMES = ("codex", "claude")
TASK_NAMES = (
    "install-skills",
    "configure-skill-config",
    "create-vault",
    "configure-clis",
    "verify-setup",
)
EXPECTED_TOP_LEVEL_DIRECTORIES = (
    "00 Kontext",
    "01 Inbox",
    "02 Projekte",
    "03 Bereiche",
    "04 Ressourcen",
    "05 Daily Notes",
    "06 Archive",
    "07 Anhänge",
)
DEFAULT_MOUNT_NAMES = ("obsidian", "obsidian_brain", ".obsidian_brain")
REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
CONFIG_PATH = SRC_DIR / "scripts" / "config.json"


def path_exists_safely(candidate_path: Path) -> bool:
    """Check whether a path exists without failing on permission errors."""
    try:
        return candidate_path.exists()
    except PermissionError:
        return False


def load_json_file(json_path: Path) -> dict:
    """Read a JSON file and return an empty dictionary when it is missing."""
    if json_path.is_file():
        with open(json_path, encoding="utf-8") as json_file:
            return json.load(json_file)
    return {}


def write_json_file(json_path: Path, data: dict) -> None:
    """Write one JSON file with deterministic formatting."""
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)
        json_file.write("\n")


def load_base_config() -> dict:
    """Load the canonical setup configuration shipped with the repository."""
    config = load_json_file(CONFIG_PATH)

    if "expected_top_level_directories" not in config:
        config["expected_top_level_directories"] = list(EXPECTED_TOP_LEVEL_DIRECTORIES)
    if "mount_names" not in config:
        config["mount_names"] = list(DEFAULT_MOUNT_NAMES)

    return config


def get_default_user_vault_root() -> Path:
    """Return the default physical vault root under the user's home."""
    return Path.home().resolve() / ".obsidian_brain"


def get_source_skill_path(tool_name: str) -> Path:
    """Return the versioned source directory for one tool."""
    source_skill_path = SRC_DIR / tool_name / SKILL_NAME

    if not source_skill_path.is_dir():
        raise FileNotFoundError(f"Missing source skill directory: {source_skill_path}")

    return source_skill_path


def get_target_skill_path(home_path: Path, tool_name: str) -> Path:
    """Build the installation target path for one tool inside one home."""
    return home_path / f".{tool_name}" / "skills" / SKILL_NAME


def derive_windows_path(candidate_path: Path) -> str:
    """Derive a Windows-style path when possible."""
    candidate_path_str = str(candidate_path)
    windows_path_match = re.match(r"^([a-zA-Z]):[\\\\/](.*)$", candidate_path_str)

    if windows_path_match is not None:
        return PureWindowsPath(candidate_path_str).as_posix()

    mount_path_match = re.match(r"^/mnt/([a-zA-Z])/(.*)$", candidate_path_str)

    if mount_path_match is not None:
        drive_letter = mount_path_match.group(1).upper()
        remaining_path = mount_path_match.group(2).replace(os.sep, "/")
        return f"{drive_letter}:/{remaining_path}"

    return ""


def derive_posix_path(candidate_path: Path) -> str:
    """Derive a POSIX-style path when possible."""
    candidate_path_str = str(candidate_path)
    windows_path_match = re.match(r"^([a-zA-Z]):[\\\\/](.*)$", candidate_path_str)

    if windows_path_match is not None:
        windows_path = PureWindowsPath(candidate_path_str)
        drive_letter = windows_path.drive[0].lower()
        relative_parts = list(windows_path.parts[1:])
        return str(PurePosixPath("/mnt", drive_letter, *relative_parts))

    return str(candidate_path.resolve())


def build_vault_roots(vault_root_path: Path) -> dict[str, str]:
    """Build platform-aware vault roots for the installed skill config."""
    vault_roots: dict[str, str] = {}
    posix_path = derive_posix_path(vault_root_path)
    windows_path = derive_windows_path(vault_root_path)

    if posix_path != "":
        vault_roots["posix"] = posix_path
    if windows_path != "":
        vault_roots["windows"] = windows_path

    if len(vault_roots) == 0:
        platform_key = "windows" if os.name == "nt" else "posix"
        vault_roots[platform_key] = str(vault_root_path)

    return vault_roots


def get_expected_vault_root_strings(vault_root_path: Path) -> set[str]:
    """Return all acceptable serialized forms of one vault root path."""
    expected_root_strings = {str(vault_root_path.resolve())}
    posix_path = derive_posix_path(vault_root_path)
    windows_path = derive_windows_path(vault_root_path)

    if posix_path != "":
        expected_root_strings.add(posix_path)
    if windows_path != "":
        expected_root_strings.add(windows_path)

    return expected_root_strings


def remove_managed_block(
    file_path: Path,
    start_marker: str,
    end_marker: str,
) -> None:
    """Remove a managed block from a file, leaving the rest intact."""
    if not file_path.is_file():
        return

    existing_text = file_path.read_text(encoding="utf-8")

    if start_marker not in existing_text or end_marker not in existing_text:
        return

    start_index = existing_text.index(start_marker)
    end_index = existing_text.index(end_marker) + len(end_marker)

    # Consume one trailing newline after end marker if present
    if end_index < len(existing_text) and existing_text[end_index] == "\n":
        end_index += 1

    before = existing_text[:start_index].rstrip()
    after = existing_text[end_index:].lstrip()

    if before and after:
        updated_text = before + "\n\n" + after
    else:
        updated_text = before + after

    file_path.write_text(updated_text, encoding="utf-8")


def upsert_managed_block(
    file_path: Path,
    start_marker: str,
    end_marker: str,
    block_body: str,
) -> None:
    """Insert or replace one managed text block inside a file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    existing_text = ""

    if file_path.is_file():
        existing_text = file_path.read_text(encoding="utf-8")

    managed_block = f"{start_marker}\n{block_body.strip()}\n{end_marker}\n"

    if start_marker in existing_text and end_marker in existing_text:
        start_index = existing_text.index(start_marker)
        end_index = existing_text.index(end_marker) + len(end_marker)
        updated_text = existing_text[:start_index] + managed_block + existing_text[end_index:]
    elif existing_text.strip() == "":
        updated_text = managed_block
    else:
        updated_text = existing_text.rstrip() + "\n\n" + managed_block

    file_path.write_text(updated_text, encoding="utf-8")
