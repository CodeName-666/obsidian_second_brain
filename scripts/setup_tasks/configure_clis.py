"""Configure Codex CLI and Claude Code to use the second brain automatically."""

from __future__ import annotations

from pathlib import Path

from setup_tasks.models import SetupOptions
from setup_tasks.shared import (
    remove_managed_block,
    upsert_managed_block,
)

MANAGED_BLOCK_START = "<!-- OBSIDIAN-SECOND-BRAIN:START -->"
MANAGED_BLOCK_END = "<!-- OBSIDIAN-SECOND-BRAIN:END -->"

TEMPLATES_VAULT_SUBPATH = Path("04 Ressourcen") / "Skills" / "obsidian-second-brain"


def _shared_block() -> str:
    """Build the shared managed block used by both Claude Code and Codex CLI."""
    return """## Obsidian Second Brain

- Always use the `obsidian-second-brain` skill for brainstorming, planning, architecture discussions, project-status work, and durable knowledge capture.
- At session start, resolve the physical vault root and read `Brain.md`.
- If present, read `04 Ressourcen/Skills/Obsidian Second Brain.md`.
- If a matching note exists in `02 Projekte/`, read it before planning, summarizing, or storing durable knowledge.
- If the user says `merk dir das`, `speicher das`, or `halte das fest`, persist the durable information in the vault instead of leaving it only in session memory.
- Persist only durable insights. Do not store transient exploration noise, raw chat logs, or duplicated knowledge.
- Ask before deleting, moving, archiving, or broadly rewriting notes.
"""


def build_claude_block() -> str:
    """Build the managed CLAUDE.md template block for Claude Code."""
    return _shared_block()


def build_codex_block() -> str:
    """Build the managed AGENTS.md template block for Codex CLI."""
    return _shared_block()


def get_templates_dir(vault_root_path: Path) -> Path:
    """Return the directory inside the vault that holds the CLI templates."""
    return vault_root_path / TEMPLATES_VAULT_SUBPATH


def configure_codex_template(vault_root_path: Path) -> Path:
    """Write the Codex AGENTS.md template into the vault."""
    templates_dir = get_templates_dir(vault_root_path)
    templates_dir.mkdir(parents=True, exist_ok=True)
    agents_path = templates_dir / "AGENTS.md"
    upsert_managed_block(
        file_path=agents_path,
        start_marker=MANAGED_BLOCK_START,
        end_marker=MANAGED_BLOCK_END,
        block_body=build_codex_block(),
    )
    print(f"Wrote codex template: {agents_path}")
    return agents_path


def configure_claude_template(vault_root_path: Path) -> Path:
    """Write the Claude CLAUDE.md template into the vault."""
    templates_dir = get_templates_dir(vault_root_path)
    templates_dir.mkdir(parents=True, exist_ok=True)
    claude_path = templates_dir / "CLAUDE.md"
    upsert_managed_block(
        file_path=claude_path,
        start_marker=MANAGED_BLOCK_START,
        end_marker=MANAGED_BLOCK_END,
        block_body=build_claude_block(),
    )
    print(f"Wrote claude template: {claude_path}")
    return claude_path


def remove_global_codex(home_path: Path) -> None:
    """Remove the managed block from the global Codex AGENTS.md if present."""
    agents_path = home_path / ".codex" / "AGENTS.md"
    remove_managed_block(
        file_path=agents_path,
        start_marker=MANAGED_BLOCK_START,
        end_marker=MANAGED_BLOCK_END,
    )
    print(f"Cleaned global codex: {agents_path}")


def remove_global_claude(home_path: Path) -> None:
    """Remove the managed block from the global Claude CLAUDE.md if present."""
    claude_path = home_path / ".claude" / "CLAUDE.md"
    remove_managed_block(
        file_path=claude_path,
        start_marker=MANAGED_BLOCK_START,
        end_marker=MANAGED_BLOCK_END,
    )
    print(f"Cleaned global claude: {claude_path}")


def print_distribution_hint(vault_root_path: Path, tool_names: tuple[str, ...]) -> None:
    """Print the final hint that explains how to use the generated templates."""
    templates_dir = get_templates_dir(vault_root_path)
    tool_files = []
    if "claude" in tool_names:
        tool_files.append(("Claude Code", templates_dir / "CLAUDE.md", "CLAUDE.md"))
    if "codex" in tool_names:
        tool_files.append(("Codex CLI", templates_dir / "AGENTS.md", "AGENTS.md"))

    print()
    print("=" * 72)
    print("Second-Brain-Trigger fuer andere Projekte")
    print("=" * 72)
    print()
    print("Die folgenden Template-Dateien wurden im Vault abgelegt:")
    for tool_label, template_path, _ in tool_files:
        print(f"  - {tool_label}: {template_path}")
    print()
    print("So verknuepfst du ein anderes Projekt mit dem Second Brain:")
    print("  1. Kopiere die passende Datei in das Root-Verzeichnis des Projekts.")
    for _, _, filename in tool_files:
        print(f"     -> {filename}")
    print("  2. Starte dort Claude Code bzw. Codex CLI.")
    print("  3. Das global installierte Skill 'obsidian-second-brain' greift")
    print("     automatisch und liest den Vault-Pfad aus seiner config.json.")
    print()
    print("Die Templates bleiben im Vault und koennen bei Bedarf erneut kopiert")
    print("werden. Spaetere Updates erreichst du ueber:")
    print("  python install.py --task configure-clis")
    print("=" * 72)


def run(options: SetupOptions) -> None:
    """Write templates into the vault and clean up any global managed blocks."""
    if "codex" in options.tool_names:
        configure_codex_template(vault_root_path=options.vault_root_path)
        for home_path in options.home_paths:
            remove_global_codex(home_path=home_path)
    if "claude" in options.tool_names:
        configure_claude_template(vault_root_path=options.vault_root_path)
        for home_path in options.home_paths:
            remove_global_claude(home_path=home_path)

    print_distribution_hint(
        vault_root_path=options.vault_root_path,
        tool_names=options.tool_names,
    )
