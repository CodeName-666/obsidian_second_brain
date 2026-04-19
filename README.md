<p align="center">
  <img src="docs/readme-hero.svg" alt="Obsidian Second Brain title banner" width="100%">
</p>

# Obsidian Second Brain

> Verbindet **Claude Code** und **Codex CLI** mit einem **Obsidian-Vault**,
> der als gemeinsames, persistentes "zweites Gehirn" fuer Entwicklungs-,
> Planungs- und Wissensarbeit dient.

Dieses Repo liefert den Installer und die Skill-Quellen. Der Vault selbst ist
die personenbezogene Wissensbasis und wird nicht hier verwaltet.

---

## Inhalt

- [Motivation](#motivation)
  - [Warum dieses Projekt?](#warum-dieses-projekt)
  - [Was es konkret loest](#was-es-konkret-loest)
  - [Vorteile auf einen Blick](#vorteile-auf-einen-blick)
  - [Typische Anwendungsfaelle](#typische-anwendungsfaelle)
- [Installation](#installation)
  - [Voraussetzungen](#voraussetzungen)
  - [Schnellstart](#schnellstart)
  - [Nicht-interaktiver Modus](#nicht-interaktiver-modus)
- [Was der Installer tut](#was-der-installer-tut)
  - [Die fuenf Tasks](#die-fuenf-tasks)
  - [Repo-Struktur](#repo-struktur)
  - [Vault-Struktur nach dem Setup](#vault-struktur-nach-dem-setup)
- [Im Einsatz](#im-einsatz)
  - [Trigger-Templates in fremden Projekten](#trigger-templates-in-fremden-projekten)
  - [Projektkontext zwischen Sessions](#projektkontext-zwischen-sessions)
  - [Vault-Aufloesung zur Laufzeit](#vault-aufloesung-zur-laufzeit)
- [Wartung](#wartung)
  - [Reparatur und Updates](#reparatur-und-updates)
  - [Skill-Wrapper regenerieren](#skill-wrapper-regenerieren)
- [Weiterfuehrende Doku](#weiterfuehrende-doku)
- [Lizenz](#lizenz)

---

## Motivation

### Warum dieses Projekt?

KI-Assistenten vergessen am Ende jeder Session alles. Wer ueber Wochen an
mehreren Projekten arbeitet, erklaert denselben Kontext immer wieder neu:
Architekturentscheidungen, offene Fragen, Schreibstil, Projektziele,
bekannte Stolperfallen.

Ein Obsidian-Vault ist ein guter Ort fuer dieses Wissen – nur spricht eine
CLI-Session nicht automatisch mit dem Vault, und ein Vault hat von sich aus
keine Regeln, wo was hingehoert.

**Dieses Repo schliesst genau diese Luecke.** Es macht einen bestehenden
oder frisch angelegten Obsidian-Vault zur autoritativen, persistenten
Wissensbasis fuer Claude Code und Codex CLI – mit klaren Routing-Regeln,
Safety-Rules und einer einheitlichen Projekt-Struktur, die beide Tools
teilen.

### Was es konkret loest

| Problem | Loesung |
|---|---|
| Kontextverlust zwischen Sessions | Skill liest beim Start `Brain.md`, die Projektnotiz und die letzten Daily Notes. Eine neue Session startet mit dem Kontext der letzten. |
| Doppelte Wissenspflege | Ein physischer Vault. Mehrere Projekt-Repos koennen ihn ueber stabile Mount-Namen einbinden – keine per-Repo-Notizfriedhoefe. |
| Unklare Ablage | `Brain.md` und `references/note-routing.md` entscheiden, wohin neue Notizen gehoeren. Trigger-Phrasen wie `merk dir das`, `speicher das`, `halte das fest` loesen gezielte Ablage aus. |
| Tool-Silos | Claude Code und Codex CLI lesen aus derselben Quelle mit denselben Regeln. Ergebnisse einer Session sind in der anderen sofort sichtbar. |
| Fragiles Onboarding in neuen Projekten | Copy-Paste einer `CLAUDE.md` bzw. `AGENTS.md` ins Projekt-Root – der Vault-Pfad bleibt ausserhalb des Projekt-Repos und wird zentral aus der Skill-Config geloest. |

### Vorteile auf einen Blick

- **Ein Vault, zwei CLIs, eine Wahrheit.** Identisches Skill-Verhalten in
  Claude Code und Codex CLI, generiert aus einer gemeinsamen
  `skill-body.md`.
- **Portabel.** Trigger-Templates enthalten keinen Vault-Pfad. Projekte
  bleiben teilbar, ohne persoenliche Dateipfade zu leaken.
- **Idempotent und reparierbar.** `install.py` laesst sich beliebig oft
  laufen, einzelne Tasks gezielt ausfuehren und Vault-Pfade nachtraeglich
  umbiegen.
- **Plattformuebergreifend.** Windows, macOS, Linux, WSL – inklusive
  automatischer Erkennung des Windows-Home unter `/mnt/c/Users/...`.
- **Klare Safety-Rules.** Das Skill fragt nach, bevor es loescht,
  verschiebt oder grossflaechig umschreibt. `Projektkompass.md` ist explizit
  als Cache markiert und wird nie zur stillen Wahrheitsquelle.
- **Drei-Stufen-Kontextmodell.** Daily Notes fuer Session-Deltas,
  kanonische Projektnotiz fuer Wahrheit, optionaler Projektkompass als
  abgeleiteter Cache fuer grosse Projekte – bewusst kein globales
  `memory/`-Verzeichnis.

### Typische Anwendungsfaelle

- **Langlaufende Entwicklungsprojekte**, in denen Architektur- und
  Status-Entscheidungen ueber Wochen konsistent bleiben sollen.
- **Brainstorming und Planung**, deren durable Insights direkt in die
  passende Projekt- oder Ressourcen-Notiz wandern – statt am Ende der
  Session zu verpuffen.
- **Werkstatt- und Research-Arbeit**, bei der technisches Wissen
  wiederverwendbar unter `04 Ressourcen/` landet, statt in einzelnen
  Chatverlaeufen vergraben zu werden.
- **Mehr-Projekt-Alltag**, in dem mehrere Repos gleichzeitig auf denselben
  Vault zugreifen und Notizen unabhaengig vom aktuellen Arbeitsverzeichnis
  erreichbar bleiben.

---

## Installation

### Voraussetzungen

- Python 3.10+ (getestet mit 3.12)
- Installiertes Claude Code und/oder Codex CLI
- Optional: bestehendes Obsidian-Vault

> Das Skript ist plattformuebergreifend (Windows, macOS, Linux, WSL).
> Unter WSL erkennt der Installer automatisch das Windows-Home unter
> `/mnt/c/Users/...` und installiert auch dorthin.

### Schnellstart

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
   - **`existing`** – vorhandenes Vault einbinden. Fehlt `Brain.md`, fragt
     der Installer, ob diese erzeugt werden soll.
4. Zusammenfassung und Bestaetigung
5. Schrittweise Ausfuehrung der Tasks

### Nicht-interaktiver Modus

```bash
python install.py \
  --tool claude \
  --home /home/user \
  --vault-root /home/user/MeinVault \
  --task install-skills \
  --task configure-skill-config
```

| Flag | Beschreibung |
|---|---|
| `--tool` | `all`, `codex` oder `claude` (Default: `all`) |
| `--home` | Ziel-Home-Verzeichnis. Mehrfach verwendbar. |
| `--vault-root` | Physischer Pfad zum Vault. Faellt zurueck auf `$OBSIDIAN_SECOND_BRAIN_ROOT` und dann auf `src/scripts/config.json`. |
| `--task` | Einzelne Tasks gezielt laufen lassen. Mehrfach verwendbar. |

---

## Was der Installer tut

### Die fuenf Tasks

| Task | Was passiert |
|---|---|
| `install-skills` | Kopiert `src/claude/obsidian-second-brain/` und `src/codex/obsidian-second-brain/` in die Home-Verzeichnisse. Fuegt `scripts/` (mit `resolve_vault_context.py` und `config.json`), `references/` und `init/` aus `src/` hinzu. |
| `configure-skill-config` | Schreibt den Vault-Pfad (Windows + POSIX) in die `config.json` der installierten Skills. |
| `create-vault` | Legt den Vault-Ordner mit allen Top-Level-Ordnern (`00 Kontext` … `07 Anhänge`), einer `README.md` und einer `Brain.md` an. Vorhandene Dateien werden nicht ueberschrieben. |
| `configure-clis` | Erzeugt im Vault unter `04 Ressourcen/Skills/obsidian-second-brain/` die Trigger-Templates `CLAUDE.md` und `AGENTS.md`. Entfernt ausserdem alte Managed-Bloecke aus globalen `~/.claude/CLAUDE.md` und `~/.codex/AGENTS.md`. |
| `verify-setup` | Prueft, ob Vault, Skill-Installationen, `config.json` und Templates korrekt vorliegen. |

### Repo-Struktur

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

### Vault-Struktur nach dem Setup

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

> Details zur Philosophie (PARA-artig, Projekte als einzelne `.md`-Datei
> bis sie Teilnotizen brauchen) stehen in der vom Installer erzeugten
> `Brain.md`. Die kanonische Vorlage liegt unter
> [`src/init/Brain.md`](src/init/Brain.md).

---

## Im Einsatz

### Trigger-Templates in fremden Projekten

Damit das Skill in einem beliebigen Projekt automatisch anspringt, liegen
im Vault zwei Copy-Paste-Vorlagen:

```
<vault>/04 Ressourcen/Skills/obsidian-second-brain/
├── CLAUDE.md      ← fuer Projekte, in denen Claude Code laeuft
└── AGENTS.md      ← fuer Projekte, in denen Codex CLI laeuft
```

**So bindet man das Skill in ein fremdes Projekt ein:**

1. Passende Datei in das Root-Verzeichnis des Projekts kopieren.
2. Claude Code oder Codex CLI in diesem Projekt starten.
3. Das global installierte Skill `obsidian-second-brain` wird automatisch
   geladen und liest den Vault-Pfad aus seiner `config.json`.

> Die Templates enthalten **keinen** Vault-Pfad. Dadurch bleiben sie
> portabel und sensible Pfade nicht in fremden Repos stecken.

### Projektkontext zwischen Sessions

Das Repo unterstuetzt ein **Drei-Stufen-Modell** fuer wiederaufnahmefaehigen
Projektkontext:

| Stufe | Rolle | Ort |
|---|---|---|
| 1. Session-Deltas | Tagesnotizen mit Entscheidungen, Problemen, naechsten Einstiegen | `05 Daily Notes/` |
| 2. Wahrheitsquelle | Kanonische Projekt-Hauptnotiz | `02 Projekte/<Projektname>.md` oder `02 Projekte/<Projektname>/<Projektname>.md` |
| 3. Abgeleiteter Cache | Optionaler Projektkompass (nur fuer grosse Projekte) | `02 Projekte/<Projektname>/Projektkompass.md` |

Ein `Projektkompass.md` entsteht nur fuer folder-basierte Projekte und nur,
wenn die Hauptnotiz mehr als 300 nichtleere Zeilen hat oder das Projekt
mehr als 3 fachliche Unternotizen ausserhalb von `Tasks/` besitzt. Die
Notiz muss Frontmatter wie `note_role: project_digest`,
`truth_source: false` und `write_policy: consolidate_only` tragen.

**Runtime-Helfer unter `src/scripts/`:**

| Skript | Zweck |
|---|---|
| [`load_project_context.py`](src/scripts/load_project_context.py) | Liefert die empfohlene Lesereihenfolge fuer Projektkontext. |
| [`persist_project_delta.py`](src/scripts/persist_project_delta.py) | Schreibt Session-Deltas in Daily Notes. |
| [`rebuild_project_kompass.py`](src/scripts/rebuild_project_kompass.py) | Erzeugt den abgeleiteten Projektkompass neu. |

### Vault-Aufloesung zur Laufzeit

Das Skript
[`src/scripts/resolve_vault_context.py`](src/scripts/resolve_vault_context.py)
wird vom Skill zur Laufzeit aufgerufen und ermittelt den aktiven Vault.
Aufloesungs-Reihenfolge:

1. Umgebungsvariable `OBSIDIAN_SECOND_BRAIN_ROOT`
2. `scripts/config.json` (vom Installer gesetzt)
3. Mount-Pattern im aktuellen Arbeitsverzeichnis (`obsidian`,
   `obsidian_brain`, `.obsidian_brain`)
4. Fallback: `~/.obsidian_brain`

> Dadurch laesst sich der Vault-Pfad auch ohne Neu-Installation verlagern,
> indem nur die `config.json` des installierten Skills angepasst wird.

---

## Wartung

### Reparatur und Updates

Der Installer ist idempotent und kann wiederholt aufgerufen werden:

```bash
# Nur Skill-Dateien neu installieren und verifizieren
python install.py --task install-skills --task verify-setup

# Nur Trigger-Templates im Vault aktualisieren
python install.py --task configure-clis

# Config auf neuen Vault-Pfad umstellen
python install.py --task configure-skill-config --vault-root /neuer/pfad
```

### Skill-Wrapper regenerieren

Die `SKILL.md`-Dateien unter `src/claude/...` und `src/codex/...` werden
aus `src/shared/skill-body.md` generiert. Nach einer Aenderung am Body:

```bash
python scripts/render_skill_wrappers.py
```

---

## Weiterfuehrende Doku

- [`docs/install-process.md`](docs/install-process.md) – detaillierte
  Task-Beschreibung, Output-Artefakte, Reparatur-Rezepte
- [`src/shared/skill-body.md`](src/shared/skill-body.md) – kanonische
  Skill-Beschreibung
- [`src/references/note-routing.md`](src/references/note-routing.md) –
  Fallback-Regeln fuer das Routing neuer Notizen, wenn `Brain.md` keine
  Antwort hat

---

## Lizenz

Dieses Repo ist als persoenliches Setup-Werkzeug gedacht. Fuer
Wiederverwendung durch andere gelten die ueblichen Spielregeln: gerne
verwenden, nicht kaputt bauen, bei Unklarheiten nachfragen.
