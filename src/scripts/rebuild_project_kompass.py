#!/usr/bin/env python3
"""Rebuild one project digest note from canonical project context."""

from __future__ import annotations

import argparse
import json

from project_context import (
    extract_list_lines,
    extract_section_markdown,
    is_migrated_project_note,
    iter_project_supporting_notes,
    note_link_target,
    now_stamp,
    project_digest_path,
    project_digest_threshold_reached,
    resolve_note_path,
    resolve_vault_root_path,
    source_gap_exists,
    wikilink_for_note,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    argument_parser = argparse.ArgumentParser(
        description="Rebuild one project digest note from canonical project context."
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
        "--days",
        type=int,
        default=7,
        help="How many recent daily notes to inspect for possible source gaps.",
    )
    argument_parser.add_argument(
        "--line-threshold",
        type=int,
        default=300,
        help="Minimum nonempty line count before a migrated project becomes digest-eligible.",
    )
    argument_parser.add_argument(
        "--note-threshold",
        type=int,
        default=3,
        help="Minimum number of supporting subnotes before a migrated project becomes digest-eligible.",
    )
    argument_parser.add_argument(
        "--force",
        action="store_true",
        help="Write the digest even when the threshold is not reached.",
    )
    return argument_parser.parse_args()


def section_or_fallback(section_markdown: str, fallback_line: str) -> str:
    """Return one section body or a fallback bullet."""
    if section_markdown.strip() != "":
        return section_markdown.strip()
    return f"- {fallback_line}"


def build_relevant_notes_lines(vault_root_path, project_note_path) -> list[str]:
    """Build the list of project sibling notes for the digest."""
    relevant_lines: list[str] = []
    for note_path in iter_project_supporting_notes(project_note_path):
        relevant_lines.append(f"- [[{note_link_target(vault_root_path, note_path)}]]")

    if relevant_lines:
        return relevant_lines

    return ["- Keine weiteren fachlichen Projektnotizen gefunden."]


def build_daily_gap_lines(vault_root_path, recent_daily_note_paths) -> list[str]:
    """Build the daily-gap section lines."""
    if recent_daily_note_paths:
        return [
            f"- [[{note_link_target(vault_root_path, note_path)}]]"
            for note_path in recent_daily_note_paths
        ]

    return ["- Keine recenten Projekt-Deltas in den letzten Tagen gefunden."]


def build_digest_text(
    vault_root_path,
    project_note_path,
    has_source_gap: bool,
    recent_daily_note_paths,
) -> str:
    """Build the complete project digest markdown."""
    project_note_text = project_note_path.read_text(encoding="utf-8")
    canonical_wikilink = wikilink_for_note(vault_root_path, project_note_path)

    current_state_markdown = extract_section_markdown(project_note_text, "Aktueller Stand")
    next_steps_markdown = extract_section_markdown(project_note_text, "Naechste sinnvolle Schritte")
    completed_markdown = extract_section_markdown(project_note_text, "Erledigt seit letztem Stand")
    completed_lines = extract_list_lines(completed_markdown, limit=8)

    frontmatter = (
        "---\n"
        "tags:\n"
        "  - projekt\n"
        "  - digest\n"
        "  - derived\n"
        "status: derived\n"
        "note_role: project_digest\n"
        "truth_source: false\n"
        f'canonical_note: "{canonical_wikilink}"\n'
        "write_policy: consolidate_only\n"
        "manual_edits: discouraged\n"
        "generated_from:\n"
        f'  - "{canonical_wikilink}"\n'
        f"generated_at: {now_stamp()}\n"
        f"source_gap: {'true' if has_source_gap else 'false'}\n"
        "---"
    )

    gap_callout = (
        "> [!warning]\n"
        "> Recent project deltas in Daily Notes may be newer than the canonical project note.\n"
        "> Refresh the main project note before trusting this cache."
        if has_source_gap
        else "> [!note]\n> Diese Notiz ist ein abgeleiteter Cache. Die kanonische Wahrheitsquelle bleibt die Hauptprojektnotiz."
    )

    completed_block = "\n".join(completed_lines) if completed_lines else "- Keine extrahierten Abschluss- oder Fortschrittsbullets gefunden."
    relevant_notes_block = "\n".join(build_relevant_notes_lines(vault_root_path, project_note_path))
    daily_gap_block = "\n".join(build_daily_gap_lines(vault_root_path, recent_daily_note_paths))

    return (
        f"{frontmatter}\n\n"
        "# Projektkompass\n\n"
        f"{gap_callout}\n\n"
        "## Aktiver Fokus\n\n"
        f"{section_or_fallback(current_state_markdown, 'Noch kein extrahierter Status vorhanden.')}\n\n"
        "## Naechster Einstieg\n\n"
        f"{section_or_fallback(next_steps_markdown, 'Noch keine extrahierten naechsten Schritte vorhanden.')}\n\n"
        "## Zuletzt belastbar geaendert\n\n"
        f"{completed_block}\n\n"
        "## Relevante Notizen\n\n"
        f"{relevant_notes_block}\n\n"
        "## Daily-Delta-Hinweise\n\n"
        f"{daily_gap_block}\n"
    )


def main() -> int:
    """Rebuild one project digest when the project is eligible."""
    arguments = parse_args()
    vault_root_path = resolve_vault_root_path(arguments.vault_root or None)
    project_note_path = resolve_note_path(vault_root_path, arguments.project_note)
    digest_path = project_digest_path(project_note_path)

    migrated_project = is_migrated_project_note(vault_root_path, project_note_path)
    threshold_reached, nonempty_line_count, supporting_note_count = project_digest_threshold_reached(
        project_note_path=project_note_path,
        line_threshold=arguments.line_threshold,
        note_threshold=arguments.note_threshold,
    )
    eligible = migrated_project and threshold_reached

    if not eligible and not arguments.force:
        report = {
            "project_note": str(project_note_path),
            "project_digest": str(digest_path),
            "eligible": False,
            "migrated_project": migrated_project,
            "nonempty_lines": nonempty_line_count,
            "supporting_notes": supporting_note_count,
            "message": "Digest threshold not reached; existing digest left untouched.",
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    has_source_gap, recent_daily_note_paths = source_gap_exists(
        vault_root_path=vault_root_path,
        project_note_path=project_note_path,
        days=arguments.days,
    )
    digest_text = build_digest_text(
        vault_root_path=vault_root_path,
        project_note_path=project_note_path,
        has_source_gap=has_source_gap,
        recent_daily_note_paths=recent_daily_note_paths,
    )
    digest_path.write_text(digest_text, encoding="utf-8")

    report = {
        "project_note": str(project_note_path),
        "project_digest": str(digest_path),
        "eligible": eligible,
        "forced": arguments.force,
        "migrated_project": migrated_project,
        "nonempty_lines": nonempty_line_count,
        "supporting_notes": supporting_note_count,
        "source_gap": has_source_gap,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
