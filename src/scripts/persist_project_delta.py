#!/usr/bin/env python3
"""Append one project delta entry to today's daily note."""

from __future__ import annotations

import argparse
import json

from project_context import (
    now_time_label,
    resolve_note_path,
    resolve_vault_root_path,
    today_stamp,
    wikilink_for_note,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    argument_parser = argparse.ArgumentParser(
        description="Append one project delta entry to today's daily note."
    )
    argument_parser.add_argument(
        "--project-note",
        required=True,
        help="Path to the canonical project note. Relative paths are resolved from the vault root.",
    )
    argument_parser.add_argument(
        "--vault-root",
        default="",
        help="Optional explicit physical vault root.",
    )
    argument_parser.add_argument(
        "--date",
        default=today_stamp(),
        help="Daily-note date stamp in YYYY-MM-DD format. Defaults to today.",
    )
    argument_parser.add_argument(
        "--time",
        default=now_time_label(),
        help="Entry time label in HH:MM format. Defaults to the current time.",
    )
    argument_parser.add_argument("--summary", required=True, help="Short summary of the delta.")
    argument_parser.add_argument("--problem", action="append", default=[], help="Observed problem.")
    argument_parser.add_argument(
        "--decision",
        action="append",
        default=[],
        help="Decision or direction taken during the session.",
    )
    argument_parser.add_argument(
        "--changed",
        action="append",
        default=[],
        help="Concrete change made during the session.",
    )
    argument_parser.add_argument(
        "--open-thread",
        action="append",
        default=[],
        help="Open thread that remains unresolved.",
    )
    argument_parser.add_argument(
        "--next-step",
        action="append",
        default=[],
        help="Next durable step worth carrying into the next session.",
    )
    return argument_parser.parse_args()


def build_daily_note_prefix(date_stamp: str) -> str:
    """Build the initial daily-note content."""
    return (
        "---\n"
        "tags:\n"
        "  - daily-note\n"
        f"date: {date_stamp}\n"
        "---\n\n"
        f"# {date_stamp}\n"
    )


def build_entry_lines(arguments: argparse.Namespace, project_wikilink: str) -> list[str]:
    """Build one daily-delta entry as a list of lines."""
    entry_lines = [
        f"### {project_wikilink} {arguments.time}",
        f"- Summary: {arguments.summary}",
    ]

    for problem in arguments.problem:
        entry_lines.append(f"- Problem: {problem}")
    for decision in arguments.decision:
        entry_lines.append(f"- Decision: {decision}")
    for changed in arguments.changed:
        entry_lines.append(f"- Changed: {changed}")
    for open_thread in arguments.open_thread:
        entry_lines.append(f"- Open Thread: {open_thread}")
    for next_step in arguments.next_step:
        entry_lines.append(f"- Next Step: {next_step}")

    entry_lines.append(f"- Source Note: {project_wikilink}")
    return entry_lines


def append_entry(daily_note_text: str, entry_markdown: str) -> str:
    """Append one entry to the daily note, creating the delta heading when needed."""
    stripped_text = daily_note_text.rstrip()
    if "## Projekt-Deltas" not in stripped_text:
        if stripped_text != "":
            stripped_text += "\n\n"
        stripped_text += "## Projekt-Deltas\n"

    return stripped_text + "\n\n" + entry_markdown.rstrip() + "\n"


def main() -> int:
    """Append one project delta to the selected daily note."""
    arguments = parse_args()
    vault_root_path = resolve_vault_root_path(arguments.vault_root or None)
    project_note_path = resolve_note_path(vault_root_path, arguments.project_note)
    project_wikilink = wikilink_for_note(vault_root_path, project_note_path)

    daily_note_path = vault_root_path / "05 Daily Notes" / f"{arguments.date}.md"
    if daily_note_path.is_file():
        daily_note_text = daily_note_path.read_text(encoding="utf-8")
    else:
        daily_note_path.parent.mkdir(parents=True, exist_ok=True)
        daily_note_text = build_daily_note_prefix(arguments.date)

    entry_markdown = "\n".join(build_entry_lines(arguments, project_wikilink))
    updated_daily_note_text = append_entry(daily_note_text, entry_markdown)
    daily_note_path.write_text(updated_daily_note_text, encoding="utf-8")

    report = {
        "daily_note": str(daily_note_path),
        "project_note": str(project_note_path),
        "project_wikilink": project_wikilink,
        "entry_time": arguments.time,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
