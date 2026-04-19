#!/usr/bin/env python3
"""Shared helpers for project-context scripts in the Obsidian second brain."""

from __future__ import annotations

from datetime import date, datetime, timedelta
import re
from pathlib import Path

from resolve_vault_context import resolve_vault_root

PROJECT_DIGEST_FILENAME = "Projektkompass.md"
DAILY_NOTES_DIRECTORY_NAME = "05 Daily Notes"
PROJECTS_DIRECTORY_NAME = "02 Projekte"
WORKFLOW_NOTE_SUBPATH = Path("04 Ressourcen") / "Skills" / "Obsidian Second Brain.md"

FRONTMATTER_DELIMITER = "---"
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
DATE_STAMP_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def resolve_vault_root_path(explicit_vault_root: str | None) -> Path:
    """Resolve the physical vault root from an explicit path or local context."""
    if explicit_vault_root is not None and explicit_vault_root.strip() != "":
        return Path(explicit_vault_root).expanduser().resolve()

    _, vault_root_path = resolve_vault_root(Path.cwd())
    return vault_root_path


def resolve_note_path(vault_root_path: Path, note_path_value: str) -> Path:
    """Resolve one note path relative to the vault when needed."""
    note_path = Path(note_path_value).expanduser()
    if not note_path.is_absolute():
        note_path = vault_root_path / note_path

    resolved_note_path = note_path.resolve()
    resolved_note_path.relative_to(vault_root_path)
    return resolved_note_path


def project_root_directory(vault_root_path: Path) -> Path:
    """Return the vault directory that stores active projects."""
    return vault_root_path / PROJECTS_DIRECTORY_NAME


def is_migrated_project_note(vault_root_path: Path, project_note_path: Path) -> bool:
    """Return whether the project uses the folder-based canonical note layout."""
    return project_note_path.parent != project_root_directory(vault_root_path)


def project_digest_path(project_note_path: Path) -> Path:
    """Return the canonical digest path next to the project main note."""
    return project_note_path.parent / PROJECT_DIGEST_FILENAME


def note_link_target(vault_root_path: Path, note_path: Path) -> str:
    """Return the Obsidian link target for a note path inside the vault."""
    relative_note_path = note_path.relative_to(vault_root_path)

    if relative_note_path.parts[:1] == (PROJECTS_DIRECTORY_NAME,):
        project_relative_path = relative_note_path.relative_to(PROJECTS_DIRECTORY_NAME)
        if (
            len(project_relative_path.parts) == 2
            and project_relative_path.name == f"{project_relative_path.parent.name}.md"
        ):
            return project_relative_path.parent.name
        return str(project_relative_path.with_suffix("")).replace("\\", "/")

    return str(relative_note_path.with_suffix("")).replace("\\", "/")


def wikilink_for_note(vault_root_path: Path, note_path: Path) -> str:
    """Return an Obsidian wikilink for one note path."""
    return f"[[{note_link_target(vault_root_path, note_path)}]]"


def count_nonempty_lines(text: str) -> int:
    """Count all nonempty lines in a note body."""
    return sum(1 for line in text.splitlines() if line.strip() != "")


def iter_project_supporting_notes(project_note_path: Path) -> list[Path]:
    """Return project notes that are not the main note, digest, or tasks."""
    project_directory_path = project_note_path.parent
    supporting_note_paths: list[Path] = []

    for note_path in sorted(project_directory_path.rglob("*.md")):
        if note_path in (project_note_path, project_digest_path(project_note_path)):
            continue

        relative_note_path = note_path.relative_to(project_directory_path)
        if "Tasks" in relative_note_path.parts:
            continue

        supporting_note_paths.append(note_path)

    return supporting_note_paths


def extract_section_markdown(note_text: str, heading_name: str) -> str:
    """Extract one markdown section body without the heading line."""
    normalized_heading_name = normalize_heading(heading_name)
    collected_lines: list[str] = []
    is_capturing = False
    heading_level = 0

    for line in note_text.splitlines():
        heading_match = HEADING_PATTERN.match(line)

        if heading_match is not None:
            current_heading_level = len(heading_match.group(1))
            current_heading_name = normalize_heading(heading_match.group(2))

            if is_capturing and current_heading_level <= heading_level:
                break

            if current_heading_name == normalized_heading_name:
                is_capturing = True
                heading_level = current_heading_level
                continue

        if is_capturing:
            collected_lines.append(line)

    return "\n".join(trim_blank_lines(collected_lines)).strip()


def normalize_heading(heading_name: str) -> str:
    """Normalize a heading name for fuzzy heading comparisons."""
    collapsed_heading = " ".join(heading_name.strip().casefold().split())
    return collapsed_heading


def trim_blank_lines(lines: list[str]) -> list[str]:
    """Trim blank lines at the start and end of a line list."""
    start_index = 0
    end_index = len(lines)

    while start_index < end_index and lines[start_index].strip() == "":
        start_index += 1

    while end_index > start_index and lines[end_index - 1].strip() == "":
        end_index -= 1

    return lines[start_index:end_index]


def extract_list_lines(section_markdown: str, limit: int) -> list[str]:
    """Extract flat list items from a markdown section."""
    list_lines: list[str] = []
    for line in section_markdown.splitlines():
        stripped_line = line.strip()
        if stripped_line.startswith("- "):
            list_lines.append(stripped_line)
        elif re.match(r"^\d+\.\s", stripped_line):
            list_lines.append(stripped_line)

        if len(list_lines) >= limit:
            break

    return list_lines


def recent_daily_note_paths(vault_root_path: Path, days: int) -> list[Path]:
    """Return recent daily-note paths sorted newest first."""
    earliest_date = date.today() - timedelta(days=max(days - 1, 0))
    daily_notes_directory_path = vault_root_path / DAILY_NOTES_DIRECTORY_NAME
    note_date_pairs: list[tuple[date, Path]] = []

    if not daily_notes_directory_path.is_dir():
        return []

    for note_path in daily_notes_directory_path.glob("*.md"):
        if not DATE_STAMP_PATTERN.match(note_path.stem):
            continue

        note_date = date.fromisoformat(note_path.stem)
        if note_date >= earliest_date:
            note_date_pairs.append((note_date, note_path))

    return [note_path for _, note_path in sorted(note_date_pairs, reverse=True)]


def matching_daily_note_paths(
    vault_root_path: Path,
    project_note_path: Path,
    days: int,
) -> list[Path]:
    """Return recent daily notes that mention the project note."""
    project_wikilink = wikilink_for_note(vault_root_path, project_note_path)
    project_stem = project_note_path.stem
    matching_note_paths: list[Path] = []

    for daily_note_path in recent_daily_note_paths(vault_root_path, days):
        daily_note_text = daily_note_path.read_text(encoding="utf-8")
        if project_wikilink in daily_note_text or f"[[{project_stem}]]" in daily_note_text:
            matching_note_paths.append(daily_note_path)

    return matching_note_paths


def project_digest_threshold_reached(
    project_note_path: Path,
    line_threshold: int,
    note_threshold: int,
) -> tuple[bool, int, int]:
    """Return whether the digest threshold is reached plus both measured values."""
    main_note_text = project_note_path.read_text(encoding="utf-8")
    nonempty_line_count = count_nonempty_lines(main_note_text)
    supporting_note_count = len(iter_project_supporting_notes(project_note_path))
    is_eligible = (
        nonempty_line_count > line_threshold or supporting_note_count > note_threshold
    )
    return is_eligible, nonempty_line_count, supporting_note_count


def source_gap_exists(
    vault_root_path: Path,
    project_note_path: Path,
    days: int,
) -> tuple[bool, list[Path]]:
    """Return whether recent daily deltas may be newer than the project main note."""
    main_note_mtime = project_note_path.stat().st_mtime
    matching_note_paths = matching_daily_note_paths(
        vault_root_path=vault_root_path,
        project_note_path=project_note_path,
        days=days,
    )
    has_gap = any(note_path.stat().st_mtime > main_note_mtime for note_path in matching_note_paths)
    return has_gap, matching_note_paths


def workflow_note_path(vault_root_path: Path) -> Path:
    """Return the shared workflow note path inside the vault."""
    return vault_root_path / WORKFLOW_NOTE_SUBPATH


def today_stamp() -> str:
    """Return today's ISO date stamp."""
    return date.today().isoformat()


def now_stamp() -> str:
    """Return the current local timestamp without timezone suffix."""
    return datetime.now().isoformat(timespec="seconds")


def now_time_label() -> str:
    """Return the current local time label for daily deltas."""
    return datetime.now().strftime("%H:%M")


def read_frontmatter_scalars(note_path: Path) -> dict[str, str]:
    """Read simple frontmatter scalars from one note."""
    note_text = note_path.read_text(encoding="utf-8")
    if not note_text.startswith(FRONTMATTER_DELIMITER + "\n"):
        return {}

    lines = note_text.splitlines()
    scalars: dict[str, str] = {}
    for line in lines[1:]:
        if line == FRONTMATTER_DELIMITER:
            break

        if ":" not in line or line.startswith("  "):
            continue

        key, value = line.split(":", 1)
        scalars[key.strip()] = value.strip().strip('"')

    return scalars
