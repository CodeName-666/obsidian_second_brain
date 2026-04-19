#!/usr/bin/env python3
"""Print the ordered second-brain context for one project note."""

from __future__ import annotations

import argparse
import json

from project_context import (
    matching_daily_note_paths,
    project_digest_path,
    read_frontmatter_scalars,
    resolve_note_path,
    resolve_vault_root_path,
    wikilink_for_note,
    workflow_note_path,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    argument_parser = argparse.ArgumentParser(
        description="Print the ordered second-brain context for one project note."
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
        help="How many recent daily notes to inspect for matching project deltas.",
    )
    return argument_parser.parse_args()


def main() -> int:
    """Resolve and print the ordered project context as JSON."""
    arguments = parse_args()
    vault_root_path = resolve_vault_root_path(arguments.vault_root or None)
    project_note_path = resolve_note_path(vault_root_path, arguments.project_note)
    digest_path = project_digest_path(project_note_path)
    workflow_path = workflow_note_path(vault_root_path)
    daily_note_paths = matching_daily_note_paths(
        vault_root_path=vault_root_path,
        project_note_path=project_note_path,
        days=arguments.days,
    )

    context_order = [
        {"kind": "brain", "path": str(vault_root_path / "Brain.md")},
    ]

    if workflow_path.is_file():
        context_order.append({"kind": "workflow", "path": str(workflow_path)})

    digest_frontmatter = read_frontmatter_scalars(digest_path) if digest_path.is_file() else {}
    if digest_path.is_file():
        context_order.append(
            {
                "kind": "project_digest",
                "path": str(digest_path),
                "truth_source": digest_frontmatter.get("truth_source", ""),
                "note_role": digest_frontmatter.get("note_role", ""),
            }
        )

    context_order.append({"kind": "project_note", "path": str(project_note_path)})

    for daily_note_path in daily_note_paths:
        context_order.append({"kind": "daily_note", "path": str(daily_note_path)})

    report = {
        "vault_root": str(vault_root_path),
        "project_note": str(project_note_path),
        "project_wikilink": wikilink_for_note(vault_root_path, project_note_path),
        "project_digest": str(digest_path),
        "digest_exists": digest_path.is_file(),
        "daily_note_days": arguments.days,
        "context_order": context_order,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
