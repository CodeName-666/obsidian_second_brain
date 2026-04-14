"""Configure Codex CLI and Claude Code to use the second brain automatically."""

from __future__ import annotations

from pathlib import Path

from setup_tasks.models import SetupOptions
from setup_tasks.shared import upsert_managed_block

MANAGED_BLOCK_START = "<!-- OBSIDIAN-SECOND-BRAIN:START -->"
MANAGED_BLOCK_END = "<!-- OBSIDIAN-SECOND-BRAIN:END -->"


def build_managed_block(vault_root_path: Path) -> str:
    """Build the managed CLAUDE.md / AGENTS.md block.

    Intentionally minimal: the `obsidian-second-brain` skill description handles
    discovery, and the skill body carries the operational rules. This block only
    pins the vault root so tools can skip the resolver when the path is stable.
    """
    return f"""## Obsidian Second Brain

Vault root: `{vault_root_path}`.
"""


def build_codex_block(vault_root_path: Path) -> str:
    """Build the managed AGENTS.md block for Codex."""
    return build_managed_block(vault_root_path)


def build_claude_block(vault_root_path: Path) -> str:
    """Build the managed CLAUDE.md block for Claude Code."""
    return build_managed_block(vault_root_path)


def configure_codex(home_path: Path, vault_root_path: Path) -> None:
    """Insert or update the managed Codex AGENTS.md block."""
    agents_path = home_path / ".codex" / "AGENTS.md"
    upsert_managed_block(
        file_path=agents_path,
        start_marker=MANAGED_BLOCK_START,
        end_marker=MANAGED_BLOCK_END,
        block_body=build_codex_block(vault_root_path),
    )
    print(f"Configured codex:{agents_path}")


def configure_claude(home_path: Path, vault_root_path: Path) -> None:
    """Insert or update the managed Claude CLAUDE.md block."""
    claude_path = home_path / ".claude" / "CLAUDE.md"
    upsert_managed_block(
        file_path=claude_path,
        start_marker=MANAGED_BLOCK_START,
        end_marker=MANAGED_BLOCK_END,
        block_body=build_claude_block(vault_root_path),
    )
    print(f"Configured claude:{claude_path}")


def run(options: SetupOptions) -> None:
    """Configure all requested CLI homes to use the second brain automatically."""
    for home_path in options.home_paths:
        if "codex" in options.tool_names:
            configure_codex(home_path=home_path, vault_root_path=options.vault_root_path)
        if "claude" in options.tool_names:
            configure_claude(home_path=home_path, vault_root_path=options.vault_root_path)
