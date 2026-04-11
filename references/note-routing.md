# Note Routing

Use this file only after reading `Brain.md`. `Brain.md` stays authoritative when the two differ.

## Route content by durability

- `00 Kontext/`: Store durable personal or cross-project context such as writing style, positioning, branding, or standing working preferences.
- `01 Inbox/`: Store raw, not-yet-sorted thoughts, fragments, and quick captures that still need triage.
- `02 Projekte/`: Store active project knowledge, architecture notes, ticket notes, project plans, and project-specific technical findings.
- `03 Bereiche/`: Store ongoing responsibilities without a defined end date. Create or extend this area only when the content is truly long-lived.
- `04 Ressourcen/`: Store reusable technical knowledge, workflow notes, MCP or tool documentation, skill documentation, and reference material that outlives a single project.
- `05 Daily Notes/`: Store session summaries, daily logs, and chronologically organized working notes.
- `06 Archive/`: Store inactive or completed material only when the user explicitly wants archival movement.
- `07 Anhänge/`: Store binary attachments and embedded files.

## Choose the canonical note

- Update the most specific existing note before creating a new one.
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
