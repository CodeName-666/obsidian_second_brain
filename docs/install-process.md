# Install Process

This file documents the structured installation and setup flow for `obsidian-second-brain`.

## Goal

The setup should leave the user with:

- the installed `obsidian-second-brain` skill for Codex CLI and Claude Code
- a configured vault root for the installed skill copies
- a usable Obsidian vault with `README.md` and `Brain.md`
- global CLI instructions that make the second brain part of the default workflow
- a verification step that confirms the setup artifacts exist

## Entry Point

The entry point is:

- `scripts/install.py`

Behavior:

- without parameters: starts an interactive wizard
- with parameters: runs non-interactively and can target specific tasks

## Task Order

The setup runs these tasks in order:

1. `install-skills`
2. `configure-skill-config`
3. `create-vault`
4. `configure-clis`
5. `verify-setup`

## Shared Skill Source

The Codex and Claude skill wrappers are generated from one canonical source.

Current structure:

- `shared/skill-body.md` is the canonical markdown body
- `scripts/setup_tasks/skill_renderer.py` renders the `SKILL.md` content
- `scripts/render_skill_wrappers.py` regenerates the repo-local wrappers under
  `claude/obsidian-second-brain/SKILL.md` and `codex/obsidian-second-brain/SKILL.md`

Both tools share identical frontmatter (`name`, `description`) and body, so the
two rendered wrappers are byte-identical. They are still written to two separate
locations because each tool installs from its own source tree and Codex ships an
extra sidecar at `codex/obsidian-second-brain/agents/openai.yaml` that Claude
does not need.

## Task Responsibilities

### `install-skills`

Installs the versioned skill files into the selected homes for:

- `~/.codex/skills/obsidian-second-brain/`
- `~/.claude/skills/obsidian-second-brain/`

This task copies:

- the tool-specific `SKILL.md`
- shared files from `scripts/`
- shared files from `references/`
- bootstrap material from `init/`

### `configure-skill-config`

Writes the installed `scripts/config.json` files so the installed skill copies point to the selected physical vault root.

Configured values include:

- `vault_roots`
- `expected_top_level_directories`
- `mount_names`

Default behavior:

- when no explicit vault root is passed, the setup defaults to `~/.obsidian_brain`
- this default can still be overridden via `--vault-root`
- the wizard also proposes this location by default and allows changing it

### `create-vault`

Creates or completes the physical Obsidian vault:

- top-level folder structure
- `README.md`
- `Brain.md`

The task is conservative:

- existing files are not overwritten
- missing directories are created
- missing bootstrap files are added

### `configure-clis`

Configures Codex CLI and Claude Code to use the second brain automatically by maintaining managed blocks in:

- `~/.codex/AGENTS.md`
- `~/.claude/CLAUDE.md`

These blocks tell the tools to:

- load `Brain.md`
- read the shared workflow note
- use the vault for durable knowledge capture
- prefer canonical notes over duplicated memory

### `verify-setup`

Checks that the expected setup artifacts exist:

- installed skill directories
- installed `SKILL.md`
- installed `scripts/config.json`
- installed runtime references (`references/note-routing.md`)
- global CLI instruction files with managed blocks
- vault root, `README.md`, `Brain.md`
- expected top-level vault directories

## Interactive Mode

Run:

```bash
python3 scripts/install.py
```

The wizard guides the user through:

1. tool selection
2. home directory selection
3. vault-root selection
4. setup summary
5. step-by-step execution with confirmation before each task

## Non-Interactive Mode

Run:

```bash
python3 scripts/install.py --home /path/to/home --vault-root /path/to/vault
```

Examples:

```bash
python3 scripts/install.py --tool codex --home /home/user --vault-root /home/user/.obsidian_brain

python3 scripts/install.py \
  --home /home/user \
  --home /mnt/c/Users/NoName \
  --vault-root /home/user/.obsidian_brain

python3 scripts/install.py \
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
- `~/.codex/AGENTS.md`
- `~/.claude/CLAUDE.md`
- `<vault-root>/README.md`
- `<vault-root>/Brain.md`
- `<vault-root>/00 Kontext/`
- `<vault-root>/01 Inbox/`
- `<vault-root>/02 Projekte/`
- `<vault-root>/04 Ressourcen/`

## Repair Usage

The setup can also be used as a repair flow.

Typical repair calls:

```bash
python3 scripts/install.py \
  --home /home/user \
  --vault-root /home/user/.obsidian_brain \
  --task configure-skill-config \
  --task configure-clis \
  --task verify-setup
```

## Limits

Current scope:

- installs the versioned local `obsidian-second-brain` skill
- configures Codex CLI and Claude Code global instruction files
- bootstraps the vault structure and verifies the result

Not yet covered automatically:

- downloading unrelated helper skills from external repositories
- generating project-local `AGENTS.md` or `CLAUDE.md` files for arbitrary repos
- installing optional Codex hook files
