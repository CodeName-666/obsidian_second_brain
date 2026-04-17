"""Create or complete the Obsidian vault used as the second brain."""

from __future__ import annotations

from pathlib import Path

from setup_tasks.models import SetupOptions
from setup_tasks.shared import SRC_DIR, load_base_config

BRAIN_TEMPLATE_PATH = SRC_DIR / "init" / "Brain.md"


def build_readme_content() -> str:
    """Build the initial vault README."""
    return """# Obsidian Second Brain

Dieses Vault wurde durch das Setup von `obsidian-second-brain` initialisiert.

## Einstieg

- `Brain.md` ist die zentrale Routing- und Kontextdatei fuer KI-gestuetzte Arbeit.
- `00 Kontext/` enthaelt persoenliches und projektuebergreifendes Dauerwissen.
- `01 Inbox/` ist fuer unsortierte Gedanken.
- `02 Projekte/` enthaelt aktive Projekte.
- `04 Ressourcen/` enthaelt wiederverwendbares Wissen und Skill-Dokumentation.

## Naechste Schritte

1. `Brain.md` pruefen und auf dein Setup anpassen.
2. Relevante Projekt- und Kontextnotizen anlegen.
3. Codex CLI und Claude Code mit dem Second Brain verbinden.
"""


def load_brain_template() -> str:
    """Load the canonical generic Brain.md template from src/init/."""
    return BRAIN_TEMPLATE_PATH.read_text(encoding="utf-8")


def write_file_if_missing(file_path: Path, content: str) -> None:
    """Create one file only when it does not already exist."""
    if not file_path.exists():
        file_path.write_text(content, encoding="utf-8")


def run(options: SetupOptions) -> None:
    """Create the vault root, top-level folders, README, and Brain.md."""
    config = load_base_config()
    expected_directories = config.get("expected_top_level_directories", [])
    vault_root_path = options.vault_root_path
    vault_root_path.mkdir(parents=True, exist_ok=True)

    for directory_name in expected_directories:
        (vault_root_path / directory_name).mkdir(parents=True, exist_ok=True)

    write_file_if_missing(vault_root_path / "README.md", build_readme_content())
    write_file_if_missing(vault_root_path / "Brain.md", load_brain_template())
    print(f"Prepared vault:{vault_root_path}")
