# Note Routing

Use this file only after reading `Brain.md`. `Brain.md` stays authoritative when the two differ.

## Route content by durability

- `00 Kontext/`: Store durable personal or cross-project context such as writing style, positioning, branding, or standing working preferences.
- `01 Inbox/`: Store raw, not-yet-sorted thoughts, fragments, and quick captures that still need triage.
- `02 Projekte/`: Store active project knowledge, architecture notes, ticket notes, project plans, and project-specific technical findings.
- `02 Projekte/<Projektname>/Projektkompass.md`: Store an optional derived project digest only for migrated and sufficiently large projects. This note stays a cache and never becomes the truth source.
- `03 Bereiche/`: Store ongoing responsibilities without a defined end date. Create or extend this area only when the content is truly long-lived.
- `04 Ressourcen/`: Store reusable technical knowledge, workflow notes, MCP or tool documentation, skill documentation, and reference material that outlives a single project.
- `05 Daily Notes/`: Store session summaries, daily logs, and chronologically organized working notes, especially project deltas that should be revisited in the next session.
- `06 Archive/`: Store inactive or completed material only when the user explicitly wants archival movement.
- `07 Anhänge/`: Store binary attachments and embedded files.

## Choose the canonical note

- Update the most specific existing note before creating a new one.
- In `02 Projekte/`, the canonical project note is either `Projektname.md` for small projects or `Projektname/Projektname.md` after a project was expanded into a folder.
- When a project is migrated into a folder, move the existing main note into that folder and do not keep a duplicate top-level `Projektname.md`.
- `Projektkompass.md` is only allowed as a derived cache for a migrated project whose main note exceeds 300 nonempty lines or whose project tree has more than 3 supporting subnotes outside `Tasks/`.
- When `Projektkompass.md` exists, it must carry metadata such as `note_role: project_digest`, `truth_source: false`, and `write_policy: consolidate_only`.
- Add wikilinks instead of duplicating the same content into multiple notes.
- Keep project-specific implementation details inside the owning project tree, even if the insight came from another repo context.
- Place ticket notes under the matching project's `Tickets/` folder when that project already uses ticket subfolders.

## Maintain Brain.md

Update `Brain.md` when any of these are true:

- The top-level vault structure changed or a documented folder name drifted from reality.
- A new repo mount pattern or path convention became permanent.
- The vault purpose changed, for example from one project to a broader development knowledge base.
- A durable routing rule or exception is repeated often enough that future sessions need it.

## Ask before acting

- Ask before deleting, archiving, moving, or merging existing notes.
- Ask when two destinations are equally plausible and the choice changes long-term structure.
- Ask before creating a new top-level folder or renaming a structural folder.
