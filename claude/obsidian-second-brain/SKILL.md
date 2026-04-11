---
name: obsidian-second-brain
description: Maintain and use the user's central Obsidian development vault as a second brain. Use when Claude needs to read `Brain.md` first, capture or update development knowledge, route information into the correct vault note or folder, refine `Brain.md`, or flag structural issues in a vault mounted directly or via `obsidian/` or `.obsidian/` symlink.
disable-model-invocation: true
---

# Obsidian Second Brain

Use this skill when working on the user's Obsidian vault as a durable development knowledge system.

## Default Routine

1. Run the local resolver script at `scripts/resolve_vault_context.py`.
2. Read the resolved `Brain.md` before planning any vault change.
3. If present, read `04 Ressourcen/Skills/Obsidian Second Brain.md` from the resolved vault root as the shared cross-tool workflow note.
4. Work against the physical vault root, not a repo-specific assumption.
5. Ask when placement is ambiguous or when an action would delete, archive, move, or overwrite existing knowledge.

## Work Modes

### Capture or update knowledge

- Read the target note before editing it.
- Route content with `Brain.md` first.
- Prefer wikilinks for vault-internal references.
- Keep filenames readable with spaces and normal capitalization.
- Preserve existing frontmatter conventions where the surrounding note style already uses them.

### Retrieve context

- Start with `Brain.md`.
- Then read the project, resource, daily, or ticket notes that `Brain.md` points to.
- Prefer active project notes, recent daily notes, and linked ticket notes over broad vault searches.

### Improve vault hygiene

- Compare `Brain.md` against the real top-level structure returned by the resolver script.
- Flag structural drift, stale repo paths, duplicate placement rules, or notes that obviously belong elsewhere.
- Make small factual `Brain.md` corrections directly when the vault state proves them.
- Offer improvement suggestions when the problem is architectural or subjective.

## Safety Rules

- Never delete or move notes without explicit permission.
- Never rewrite a broad section of the vault when a targeted note update is enough.
- If the user says "merk dir das" or "speicher das", treat it as a routing task and persist the information in the most specific durable note.
- If information belongs in multiple places, update the canonical note and add links instead of duplicating full content.
