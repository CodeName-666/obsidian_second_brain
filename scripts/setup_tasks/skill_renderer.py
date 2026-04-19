"""Render tool-specific SKILL.md files from one shared canonical body."""

from __future__ import annotations

from pathlib import Path

from setup_tasks.shared import SKILL_NAME, SRC_DIR

SKILL_DESCRIPTION = (
    "Treat the user's Obsidian development vault as the authoritative second brain. "
    "Use this skill proactively for brainstorming, planning, architecture discussions, "
    "project-status work, durable knowledge capture, and phrases like `merk dir das`, "
    "`speicher das`, or `halte das fest`. Always resolve the physical vault root, read "
    "`Brain.md` first, and route durable insights into the right note instead of leaving "
    "them only in session memory."
)


def get_shared_skill_body_path() -> Path:
    """Return the canonical shared skill-body path."""
    return SRC_DIR / "shared" / "skill-body.md"


def load_shared_skill_body() -> str:
    """Load the shared markdown body for the skill."""
    return get_shared_skill_body_path().read_text(encoding="utf-8").rstrip() + "\n"


def build_frontmatter(tool_name: str) -> str:
    """Build the YAML frontmatter for one concrete target tool."""
    frontmatter_lines = [
        "---",
        f"name: {SKILL_NAME}",
        f"description: {SKILL_DESCRIPTION}",
    ]

    if tool_name == "claude":
        frontmatter_lines.append("disable-model-invocation: true")

    frontmatter_lines.append("---")
    return "\n".join(frontmatter_lines)


def render_skill_text(tool_name: str) -> str:
    """Render the complete SKILL.md text for one target tool."""
    generated_notice = (
        "<!-- Generated from src/shared/skill-body.md via scripts/render_skill_wrappers.py -->"
    )
    return (
        build_frontmatter(tool_name)
        + "\n\n"
        + generated_notice
        + "\n\n"
        + load_shared_skill_body()
    )


def get_repo_skill_path(tool_name: str) -> Path:
    """Return the canonical repo wrapper path for one target tool."""
    return SRC_DIR / tool_name / SKILL_NAME / "SKILL.md"


def write_repo_skill_file(tool_name: str) -> Path:
    """Render and write one repo-local tool wrapper."""
    skill_path = get_repo_skill_path(tool_name)
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(render_skill_text(tool_name), encoding="utf-8")
    return skill_path
