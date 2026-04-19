# Obsidian Second Brain

Installer und Quellcode fuer das Skill `obsidian-second-brain`. Das Skill verbindet **Claude Code** und **Codex CLI** mit einem Obsidian-Vault, der als gemeinsames "zweites Gehirn" fuer Entwicklungs-, Planungs- und Wissensarbeit dient.

## Ueberblick

Ziel des Projekts ist ein reproduzierbarer Setup-Ablauf, der drei Dinge auf einmal erledigt:

1. **Skill installieren** – fuer Claude Code unter `~/.claude/skills/obsidian-second-brain/` und fuer Codex CLI unter `~/.codex/skills/obsidian-second-brain/`.
2. **Vault initialisieren oder einbinden** – entweder ein neues Obsidian-Vault mit Standard-Struktur anlegen oder ein bestehendes Vault registrieren.
3. **Trigger-Templates bereitstellen** – `CLAUDE.md` und `AGENTS.md` im Vault ablegen, damit sie sich per Copy-Paste in beliebige Projekte einsetzen lassen und dort automatisch das Second-Brain-Skill aktivieren.

Der Vault selbst wird nicht in diesem Repo verwaltet – er ist die personenbezogene Wissensbasis. Dieses Repo liefert nur den Installer und die Skill-Quellen.

## Repo-Struktur

```
obsidian-second-brain/
├── install.py                     ← Entry-Point (interaktiv oder per Flags)
├── docs/
│   └── install-process.md         ← Detaildokumentation des Installers
├── scripts/                       ← Installer-Code (nicht installiert)
│   ├── render_skill_wrappers.py
│   └── setup_tasks/
│       ├── cli.py
│       ├── configure_clis.py
│       ├── configure_skill_config.py
│       ├── create_vault.py
│       ├── install_skills.py
│       ├── models.py
│       ├── shared.py
│       ├── skill_renderer.py
│       ├── verify_setup.py
│       └── wizard.py
└── src/                           ← Alles, was installiert bzw. in den Vault gelegt wird
    ├── claude/obsidian-second-brain/SKILL.md
    ├── codex/obsidian-second-brain/
    │   ├── SKILL.md
    │   └── agents/openai.yaml
    ├── shared/skill-body.md       ← Kanonische Skill-Beschreibung (Single Source)
    ├── references/note-routing.md ← Fallback-Routing-Regeln
    ├── init/Brain.md              ← Generische Brain.md-Vorlage fuer frische Vaults
    └── scripts/
        ├── load_project_context.py
        ├── persist_project_delta.py
        ├── rebuild_project_kompass.py
        ├── project_context.py
        ├── resolve_vault_context.py
        └── config.json
```

## Voraussetzungen

- Python 3.10+ (getestet mit 3.12)
- Installiertes Claude Code und/oder Codex CLI
- Optional: bestehendes Obsidian-Vault

Das Skript ist plattformuebergreifend (Windows, macOS, Linux, WSL). Unter WSL erkennt der Installer automatisch das Windows-Home unter `/mnt/c/Users/...` und installiert auch dorthin.

## Schnellstart

```bash
git clone <dieses-repo>
cd obsidian-second-brain
python install.py
```

Der Wizard fuehrt durch:

1. Auswahl der Ziel-CLIs (`all` / `codex` / `claude`)
2. Auswahl der Home-Verzeichnisse (automatisch erkannt, manuell ueberschreibbar)
3. Vault-Modus:
   - **`new`** – neues Vault anlegen (Default-Pfad: `~/.obsidian_brain`)
   - **`existing`** – vorhandenes Vault einbinden. Fehlt `Brain.md`, fragt der Installer, ob diese erzeugt werden soll.
4. Zusammenfassung und Bestaetigung
5. Schrittweise Ausfuehrung der Tasks

## Nicht-interaktiver Modus

```bash
python install.py \
  --tool claude \
  --home /home/user \
  --vault-root /home/user/MeinVault \
  --task install-skills \
  --task configure-skill-config
```

Flags im Detail:

| Flag | Beschreibung |
|---|---|
| `--tool` | `all`, `codex` oder `claude` (Default: `all`) |
| `--home` | Ziel-Home-Verzeichnis. Mehrfach verwendbar. |
| `--vault-root` | Physischer Pfad zum Vault. Faellt zurueck auf `$OBSIDIAN_SECOND_BRAIN_ROOT` und dann auf `src/scripts/config.json`. |
| `--task` | Einzelne Tasks gezielt laufen lassen. Mehrfach verwendbar. |

## Die fuenf Tasks

| Task | Was passiert |
|---|---|
| `install-skills` | Kopiert `src/claude/obsidian-second-brain/` und `src/codex/obsidian-second-brain/` in die Home-Verzeichnisse. Fuegt `scripts/` (mit `resolve_vault_context.py` und `config.json`), `references/` und `init/` aus `src/` hinzu. |
| `configure-skill-config` | Schreibt den Vault-Pfad (Windows + POSIX) in die `config.json` der installierten Skills. |
| `create-vault` | Legt den Vault-Ordner mit allen Top-Level-Ordnern (`00 Kontext` … `07 Anhänge`), einer `README.md` und einer `Brain.md` an. Vorhandene Dateien werden nicht ueberschrieben. |
| `configure-clis` | Erzeugt im Vault unter `04 Ressourcen/Skills/obsidian-second-brain/` die Trigger-Templates `CLAUDE.md` und `AGENTS.md`. Entfernt ausserdem alte Managed-Bloecke aus globalen `~/.claude/CLAUDE.md` und `~/.codex/AGENTS.md`. |
| `verify-setup` | Prueft, ob Vault, Skill-Installationen, `config.json` und Templates korrekt vorliegen. |

## Trigger-Templates

Damit das Skill in einem beliebigen Projekt automatisch anspringt, liegt im Vault:

```
<vault>/04 Ressourcen/Skills/obsidian-second-brain/
├── CLAUDE.md      ← fuer Projekte, in denen Claude Code laeuft
└── AGENTS.md      ← fuer Projekte, in denen Codex CLI laeuft
```

**Nutzung in einem fremden Projekt:**

1. Passende Datei in das Root-Verzeichnis des Projekts kopieren.
2. Claude Code oder Codex CLI in diesem Projekt starten.
3. Das global installierte Skill `obsidian-second-brain` wird automatisch geladen und liest den Vault-Pfad aus seiner `config.json`.

Die Templates enthalten keinen Vault-Pfad – der Pfad kommt allein aus der Skill-Konfiguration. Dadurch bleiben die Templates portabel und sensible Pfade nicht in fremden Repos stecken.

## Projektkontext zwischen Sessions

Das Repo unterstuetzt ein Drei-Stufen-Modell fuer wiederaufnahmefaehigen Projektkontext:

1. `05 Daily Notes/` speichern Session-Deltas.
2. Die kanonische Projekt-Hauptnotiz bleibt die Wahrheitsquelle.
3. `Projektkompass.md` ist ein optionaler, abgeleiteter Cache fuer grosse migrierte Projekte.

Ein `Projektkompass.md` entsteht nur fuer folder-basierte Projekte unter `02 Projekte/<Projektname>/`, wenn die Hauptnotiz mehr als 300 nichtleere Zeilen hat oder das Projekt mehr als 3 fachliche Unternotizen ausserhalb von `Tasks/` besitzt. Die Notiz muss Frontmatter wie `note_role: project_digest`, `truth_source: false` und `write_policy: consolidate_only` tragen.

Installierbare Runtime-Helfer unter `src/scripts/`:

- `load_project_context.py` liefert die empfohlene Lesereihenfolge fuer Projektkontext.
- `persist_project_delta.py` schreibt Session-Deltas in Daily Notes.
- `rebuild_project_kompass.py` erzeugt den abgeleiteten Projektkompass neu.

## Vault-Struktur

Nach einem frischen `create-vault`-Lauf sieht der Vault so aus:

```
<vault>/
├── Brain.md                       ← Navigations- und Routing-Schicht
├── README.md
├── 00 Kontext/                    ← Persoenliches Kontext-Profil
├── 01 Inbox/                      ← Unsortierte Gedanken
├── 02 Projekte/                   ← Aktive Projekte
├── 03 Bereiche/                   ← Laufende Verantwortungsbereiche
├── 04 Ressourcen/                 ← Wiederverwendbares Wissen
│   └── Skills/obsidian-second-brain/
│       ├── CLAUDE.md              ← Trigger-Template
│       └── AGENTS.md              ← Trigger-Template
├── 05 Daily Notes/
├── 06 Archive/
└── 07 Anhänge/
```

Details zur Philosophie (PARA-artig, Projekte als einzelne `.md`-Datei bis sie Teilnotizen brauchen) stehen in der vom Installer erzeugten `Brain.md`. Die kanonische Vorlage fuer diese Datei liegt unter [`src/init/Brain.md`](src/init/Brain.md).

## Skill-Wrapper regenerieren

Die `SKILL.md`-Dateien unter `src/claude/...` und `src/codex/...` werden aus `src/shared/skill-body.md` generiert. Nach einer Aenderung am Body:

```bash
python scripts/render_skill_wrappers.py
```

## Reparatur und Updates

Der Installer ist idempotent und kann wiederholt aufgerufen werden:

```bash
# Nur Skill-Dateien neu installieren und verifizieren
python install.py --task install-skills --task verify-setup

# Nur Trigger-Templates im Vault aktualisieren
python install.py --task configure-clis

# Config auf neuen Vault-Pfad umstellen
python install.py --task configure-skill-config --vault-root /neuer/pfad
```

## Konfiguration zur Laufzeit

Das Skript [`src/scripts/resolve_vault_context.py`](src/scripts/resolve_vault_context.py) wird vom Skill zur Laufzeit aufgerufen und ermittelt den aktiven Vault. Reihenfolge der Aufloesung:

1. Umgebungsvariable `OBSIDIAN_SECOND_BRAIN_ROOT`
2. `scripts/config.json` (vom Installer gesetzt)
3. Mount-Pattern im aktuellen Arbeitsverzeichnis (`obsidian`, `obsidian_brain`, `.obsidian_brain`)
4. Fallback: `~/.obsidian_brain`

Dadurch laesst sich der Vault-Pfad auch ohne Neu-Installation verlagern, indem die `config.json` des installierten Skills angepasst wird.

Zusaetzliche Runtime-Skripte fuer Projektkontext:

- [`src/scripts/load_project_context.py`](src/scripts/load_project_context.py)
- [`src/scripts/persist_project_delta.py`](src/scripts/persist_project_delta.py)
- [`src/scripts/rebuild_project_kompass.py`](src/scripts/rebuild_project_kompass.py)

## Weiterfuehrende Doku

- [`docs/install-process.md`](docs/install-process.md) – detaillierte Task-Beschreibung, Output-Artefakte, Reparatur-Rezepte
- [`src/shared/skill-body.md`](src/shared/skill-body.md) – kanonische Skill-Beschreibung
- [`src/references/note-routing.md`](src/references/note-routing.md) – Fallback-Regeln fuer das Routing neuer Notizen, wenn `Brain.md` keine Antwort hat

## Lizenz

Dieses Repo ist als persoenliches Setup-Werkzeug gedacht. Fuer Wiederverwendung durch andere gelten die ueblichen Spielregeln: gerne verwenden, nicht kaputt bauen, bei Unklarheiten nachfragen.
