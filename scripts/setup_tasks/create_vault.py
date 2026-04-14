"""Create or complete the Obsidian vault used as the second brain."""

from __future__ import annotations

from pathlib import Path

from setup_tasks.models import SetupOptions
from setup_tasks.shared import load_base_config


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


def build_brain_content(expected_directories: list[str]) -> str:
    """Build the initial Brain.md for a freshly created vault."""
    structure_lines = "\n".join(
        f"- `{directory_name}/`: Bestandteil des Second-Brain-Setups."
        for directory_name in expected_directories
    )

    return f"""# Vault Context

Dieses Vault ist das zentrale zweite Gehirn fuer Entwicklung, Planung und dauerhafte Wissensablage.

## Vault-Struktur

{structure_lines}

## Regeln fuer dieses Vault

- Nutze `Brain.md` als Einstiegspunkt fuer Routing und Dauerwissen.
- Neue Notizen ohne klaren Platz kommen zuerst nach `01 Inbox/`.
- Projektspezifisches Wissen gehoert nach `02 Projekte/`.
- Neue Projekte starten in `02 Projekte/` als einzelne `.md`-Datei. Wenn ein Projekt Teilnotizen braucht, wird die Hauptnotiz nach `02 Projekte/<Projektname>/<Projektname>.md` verschoben und bleibt dort die kanonische Startseite.
- Wiederverwendbares Wissen und Skill-Dokumentation gehoeren nach `04 Ressourcen/`.
- Nutze Wikilinks fuer interne Verknuepfungen.
- Bevor Inhalte geloescht, verschoben oder grob ueberschrieben werden, erst pruefen und dann bestaetigen.

## Session-Routinen

### Bei Session-Start

1. `Brain.md` lesen.
2. Relevante Projekt- oder Ressourcen-Notizen laden.

### Bei Session-Ende

1. Dauerhafte Erkenntnisse in die passende Notiz uebertragen.
2. Optional `01 Inbox/` oder `05 Daily Notes/` aktualisieren.
"""


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
    write_file_if_missing(
        vault_root_path / "Brain.md",
        build_brain_content(expected_directories=expected_directories),
    )
    print(f"Prepared vault:{vault_root_path}")
