# Install Process

This file documents the structured installation and setup flow for `obsidian-second-brain`.

## Goal

The setup should leave the user with:

- the installed `obsidian-second-brain` skill for Codex CLI and Claude Code
- a configured vault root written into the installed skill copies
- a usable Obsidian vault (new or existing) with `README.md` and `Brain.md`
- portable CLI trigger templates stored inside the vault, ready to be copied into arbitrary project roots
- a verification step that confirms every expected artifact exists

## Entry Point

The entry point is:

- `install.py` (located at the repository root)

Behavior:

- without parameters: starts an interactive wizard
- with parameters: runs non-interactively and can target specific tasks

## Repo Layout

```
obsidian-second-brain/
├── install.py             ← entry point
├── docs/                  ← this documentation
├── scripts/               ← installer-only code (not installed into homes)
│   ├── render_skill_wrappers.py
│   └── setup_tasks/
└── src/                   ← everything that gets installed or copied into the vault
    ├── claude/obsidian-second-brain/SKILL.md
    ├── codex/obsidian-second-brain/
    ├── shared/skill-body.md
    ├── references/note-routing.md
    ├── init/Brain.md
    └── scripts/
        ├── resolve_vault_context.py
        └── config.json
```

Everything under `src/` is copied into the installed skill. Everything under `scripts/` stays in the repository and is only invoked locally by `install.py`.

## Task Order

The setup runs these tasks in order:

1. `install-skills`
2. `configure-skill-config`
3. `create-vault`
4. `configure-clis`
5. `verify-setup`

In the interactive wizard, `create-vault` is skipped automatically when the user points to an existing vault that already contains a `Brain.md`. If a vault exists but has no `Brain.md`, the wizard asks whether one should be created.

## Shared Skill Source

The Codex and Claude skill wrappers are generated from one canonical source.

Current structure:

- `src/shared/skill-body.md` is the canonical markdown body
- `scripts/setup_tasks/skill_renderer.py` renders the `SKILL.md` content
- `scripts/render_skill_wrappers.py` regenerates the repo-local wrappers under
  `src/claude/obsidian-second-brain/SKILL.md` and `src/codex/obsidian-second-brain/SKILL.md`

Both tools share identical frontmatter (`name`, `description`) and body, so the two rendered wrappers are byte-identical. They are still written to two separate locations because each tool installs from its own source tree and Codex ships an extra sidecar at `src/codex/obsidian-second-brain/agents/openai.yaml` that Claude does not need.

## Task Responsibilities

### `install-skills`

Installs the versioned skill files into the selected homes:

- `~/.codex/skills/obsidian-second-brain/`
- `~/.claude/skills/obsidian-second-brain/`

Copied content:

- the tool-specific `SKILL.md`
- shared files from `src/scripts/` (`resolve_vault_context.py`, `config.json`)
- shared files from `src/references/`
- bootstrap material from `src/init/`

### `configure-skill-config`

Writes the installed `scripts/config.json` files so the installed skill copies point to the selected physical vault root.

Configured values include:

- `vault_roots` (platform-aware: `windows` and `posix` entries)
- `expected_top_level_directories`
- `mount_names`

Default behavior:

- when no explicit vault root is passed, the setup uses `$OBSIDIAN_SECOND_BRAIN_ROOT`, then `src/scripts/config.json`, then `~/.obsidian_brain`
- this default can be overridden via `--vault-root`
- the wizard also proposes this location by default and allows changing it

### `create-vault`

Creates or completes the physical Obsidian vault:

- top-level folder structure (`00 Kontext` … `07 Anhänge`)
- `README.md`
- `Brain.md`

The task is conservative:

- existing files are not overwritten
- missing directories are created
- missing bootstrap files are added

When the wizard reuses an existing vault with an intact `Brain.md`, this task is skipped entirely.

### `configure-clis`

Places trigger templates inside the vault and cleans up legacy global managed blocks.

Written files (based on the selected tools):

- `<vault>/04 Ressourcen/Skills/obsidian-second-brain/CLAUDE.md`
- `<vault>/04 Ressourcen/Skills/obsidian-second-brain/AGENTS.md`

Each template contains a `<!-- OBSIDIAN-SECOND-BRAIN:START / :END -->` managed block with rules that instruct the CLI to:

- always use the `obsidian-second-brain` skill for planning and durable knowledge
- read `Brain.md` at session start
- read shared workflow notes and matching project notes before acting
- treat phrases like `merk dir das` as persistence requests

Additionally, the task removes any leftover managed block from:

- `~/.codex/AGENTS.md`
- `~/.claude/CLAUDE.md`

At the end of the task, the installer prints a deliberately prominent hint that explains how to copy the templates from the vault into arbitrary project roots.

The templates do **not** contain a vault path. The vault path lives only in the installed skill's `config.json`, which keeps the templates portable across projects.

### `verify-setup`

Checks that the expected setup artifacts exist:

- vault root, `README.md`, `Brain.md`
- all expected top-level vault directories
- installed skill directories
- installed `SKILL.md`
- installed `scripts/config.json` pointing at the selected vault root
- installed runtime references (`references/note-routing.md`)
- vault-side trigger templates (`CLAUDE.md` / `AGENTS.md` under `04 Ressourcen/Skills/obsidian-second-brain/`)

## Interactive Mode

Run:

```bash
python install.py
```

The wizard guides the user through:

1. tool selection (`all` / `codex` / `claude`)
2. home directory selection (auto-detected; under WSL also the Windows home)
3. vault mode:
   - `new` — pick a path for a fresh vault
   - `existing` — pick an existing folder; if `Brain.md` is missing, the wizard asks whether to create one
4. summary confirmation
5. step-by-step execution with a confirmation prompt before each task

## Non-Interactive Mode

Run:

```bash
python install.py --home /path/to/home --vault-root /path/to/vault
```

Examples:

```bash
python install.py --tool codex --home /home/user --vault-root /home/user/.obsidian_brain

python install.py \
  --home /home/user \
  --home /mnt/c/Users/NoName \
  --vault-root /home/user/.obsidian_brain

python install.py \
  --home /home/user \
  --vault-root /home/user/.obsidian_brain \
  --task install-skills \
  --task configure-skill-config \
  --task verify-setup
```

## Expected Outputs

After a successful full run, the setup should have produced or updated:

- `~/.codex/skills/obsidian-second-brain/`
- `~/.claude/skills/obsidian-second-brain/`
- `<vault-root>/README.md`
- `<vault-root>/Brain.md`
- `<vault-root>/00 Kontext/`
- `<vault-root>/01 Inbox/`
- `<vault-root>/02 Projekte/`
- `<vault-root>/03 Bereiche/`
- `<vault-root>/04 Ressourcen/`
- `<vault-root>/04 Ressourcen/Skills/obsidian-second-brain/CLAUDE.md`
- `<vault-root>/04 Ressourcen/Skills/obsidian-second-brain/AGENTS.md`
- `<vault-root>/05 Daily Notes/`
- `<vault-root>/06 Archive/`
- `<vault-root>/07 Anhänge/`

The legacy global files `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md` are left alone except for the removal of any previously installed managed block.

## Using the Trigger Templates in Other Projects

The vault is the single source of truth for the templates. To connect an arbitrary project to the second brain:

1. Copy `<vault>/04 Ressourcen/Skills/obsidian-second-brain/CLAUDE.md` into the root of the target project (for Claude Code).
2. Copy `<vault>/04 Ressourcen/Skills/obsidian-second-brain/AGENTS.md` into the root of the target project (for Codex CLI).
3. Start the CLI inside that project.

The managed block triggers the globally installed `obsidian-second-brain` skill, which resolves the vault path from its own installed `config.json`.

If the managed block in the templates changes (for example because `configure-clis` runs again with updated rules), the project-local copies have to be updated manually. The block is delimited by HTML comments so it can be updated in place without touching surrounding notes.

## Repair Usage

The setup can also be used as a repair flow. Each task is idempotent.

Typical repair calls:

```bash
# rewrite only the installed skill config
python install.py --task configure-skill-config --vault-root /path/to/vault

# refresh the vault-side trigger templates after updating the managed block
python install.py --task configure-clis --vault-root /path/to/vault

# reinstall skill files and verify the result
python install.py \
  --home /home/user \
  --vault-root /home/user/.obsidian_brain \
  --task install-skills \
  --task configure-skill-config \
  --task verify-setup
```

## Runtime Vault Resolution

The installed skill ships `scripts/resolve_vault_context.py`. At runtime it resolves the active vault in this order:

1. environment variable `OBSIDIAN_SECOND_BRAIN_ROOT`
2. installed `scripts/config.json` (written by `configure-skill-config`)
3. mount patterns in the current working directory (`obsidian`, `obsidian_brain`, `.obsidian_brain`)
4. fallback: `~/.obsidian_brain`

The resolver prints a JSON report with the resolved path, `Brain.md` location, and any structural drift relative to the expected top-level folders.

## Limits

Current scope:

- installs the versioned local `obsidian-second-brain` skill for Codex CLI and Claude Code
- configures the installed skill copies with the selected vault path
- bootstraps the vault structure (or attaches to an existing vault)
- writes portable trigger templates into the vault
- cleans up legacy managed blocks in global CLI instruction files
- verifies the resulting artifacts

Not covered automatically:

- downloading unrelated helper skills from external repositories
- distributing the trigger templates into project roots (copying is a deliberate manual step so users stay aware of which projects are wired to their second brain)
- installing optional Codex hook files
