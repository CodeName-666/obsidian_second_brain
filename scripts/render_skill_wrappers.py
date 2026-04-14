#!/usr/bin/env python3
"""Render the tool-specific SKILL.md wrappers from one shared source."""

from __future__ import annotations

from setup_tasks.skill_renderer import write_repo_skill_file
from setup_tasks.shared import TOOL_NAMES


def main() -> int:
    """Render all repo-local skill wrappers."""
    for tool_name in TOOL_NAMES:
        skill_path = write_repo_skill_file(tool_name)
        print(f"Rendered {tool_name}:{skill_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
