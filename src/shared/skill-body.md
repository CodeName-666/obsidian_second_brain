# Obsidian Second Brain

Use this skill to treat the user's Obsidian vault as the authoritative second brain for development work.

## Default Routine

1. Run the local resolver script at `scripts/resolve_vault_context.py`.
2. Read the returned `Brain.md` before planning any vault change.
3. If present, read `04 Ressourcen/Skills/Obsidian Second Brain.md` from the resolved vault root as the shared cross-tool workflow note.
4. Work against the physical vault root, not a repo-specific assumption.
5. For project work, prefer the canonical main note first: `02 Projekte/Projektname.md` or, after migration, `02 Projekte/Projektname/Projektname.md`.
6. If a migrated project has `Projektkompass.md` with `truth_source: false`, treat it as a derived cache only: read it before or alongside the main note, but never as the canonical truth source.
7. For recent project status, decisions, or unresolved work, also inspect matching Daily Notes from the last 3-7 days.
8. Choose the narrowest helper skill that fits the artifact:
   - Markdown notes: `obsidian-markdown`
   - `.base` files: `obsidian-bases`
   - `.canvas` files: `json-canvas`
   - Running Obsidian app or CLI automation: `obsidian-cli`
9. Prefer direct filesystem edits for deterministic note updates. Use the Obsidian CLI only when app-aware features matter.
10. Ask when placement is ambiguous or when an action would delete, archive, move, or overwrite existing knowledge.

## Proactive Triggers

- Use this skill proactively when the user brainstorms, compares ideas, plans work, discusses architecture, records project status, or asks for a durable summary.
- Treat `merk dir das`, `speicher das`, `halte das fest`, and similar phrases as explicit persistence requests.
- If a matching project note exists in `02 Projekte/`, read it before planning, summarizing, or storing durable knowledge. For expanded projects, treat `02 Projekte/<Projektname>/<Projektname>.md` as the canonical main note.
- Persist only durable insights. Do not store transient exploration noise, raw chat logs, or duplicated knowledge.

## Work Modes

### Capture or update knowledge

- Read the target note before editing it.
- Route content with `Brain.md` first. Use [references/note-routing.md](references/note-routing.md) only when `Brain.md` is silent or drifting.
- In `02 Projekte/`, start simple projects as `Projektname.md`. Once a project needs subnotes, convert it to `Projektname/Projektname.md` and move the main note into that folder instead of keeping a duplicate top-level file.
- Do not create a global `memory/` folder or raw chat-log note. The project context model has only three writable layers: Daily Notes for session deltas, canonical project notes for durable truth, and optional project digest notes that are rebuilt instead of hand-written.
- Store session deltas in `05 Daily Notes/`. Store durable project truth in the canonical project note or its owning subnotes.
- If `Projektkompass.md` exists, treat frontmatter such as `note_role: project_digest`, `truth_source: false`, and `write_policy: consolidate_only` as authoritative metadata. That note is a cache, not a source of truth.
- Only a consolidation pass should rebuild `Projektkompass.md`. Do not use routine editing or `merk dir das` requests to write directly into the digest.
- Keep filenames readable with spaces and normal capitalization.
- Preserve or add useful frontmatter such as `tags`, `status`, `date`, `erstellt`, `aktualisiert`, or `aliases` when the surrounding note style already uses them.
- Prefer wikilinks for vault-internal references. Use Markdown links only for files outside the vault.

### Retrieve context

- Start with `Brain.md`.
- Then read the project, resource, daily, or ticket notes that `Brain.md` points to.
- For project context, prefer the canonical main project note first: either `02 Projekte/Projektname.md` or, after migration, `02 Projekte/Projektname/Projektname.md`.
- For migrated and sufficiently large projects, an optional `Projektkompass.md` may exist as a derived cache. It is only expected when the project is folder-based and the main note exceeds 300 nonempty lines or the project owns more than 3 supporting subnotes.
- If the digest exists, read it for fast orientation, then confirm against the canonical main note. If the two drift, the main note wins.
- When the user asks for current status, prefer active project notes, recent daily notes, and linked ticket notes over broad vault searches.

### Improve vault hygiene

- Compare `Brain.md` against the real top-level structure returned by the resolver script.
- Flag structural drift, stale repo paths, duplicate placement rules, or notes that obviously belong elsewhere.
- Make small factual `Brain.md` corrections directly when the vault state proves them.
- Flag stale `Projektkompass.md` notes whose frontmatter is missing `truth_source: false`, whose threshold no longer applies, or whose content appears newer than the canonical project note only because the main note was not consolidated yet.
- Offer improvement suggestions when the problem is architectural or subjective.

## Brain.md Maintenance

Update `Brain.md` when any of these become true:

- A top-level folder name, routing rule, or archival rule changed.
- A new project-repo mount pattern exists.
- A durable note-placement rule emerged from repeated work.
- The document no longer reflects the vault's actual purpose or current technical anchors.

Keep `Brain.md` focused on durable structure and rules. Store project-specific content in project notes instead.

## Safety Rules

- Never delete or move notes without explicit permission.
- Never rewrite a broad section of the vault when a targeted note update is enough.
- If the user says "merk dir das" or "speicher das", treat it as a routing task and persist the information in the most specific durable note.
- If information belongs in multiple places, update the canonical note and add links instead of duplicating full content.
- If a project digest is present, never let it silently become the truth source. Update the main note first, then rebuild the digest.

## Resources

- `scripts/resolve_vault_context.py`: Resolve the physical vault root, `Brain.md` path, and current top-level structure.
- `scripts/load_project_context.py`: Print the ordered project context, including digest and recent Daily Notes.
- `scripts/persist_project_delta.py`: Append one durable session delta to a Daily Note.
- `scripts/rebuild_project_kompass.py`: Rebuild `Projektkompass.md` from the canonical project note and recent Daily Notes.
- [references/note-routing.md](references/note-routing.md): Fallback routing and maintenance checklist when `Brain.md` needs reinforcement.
