# Codex Project Instructions

## Standing user rules

- Edit README files only when the user explicitly requests a README change.
  General development, documentation, cleanup, merge, push or release requests
  do not authorize README edits. This rule was set on 10 November 2026.
- Do not create, regenerate, edit, or schedule videos or presentations. This
  includes demo movies, narrated clips, slide decks, PowerPoint and PDF decks.
  The user explicitly set this rule on 8 November 2026. Only an explicit user
  instruction revoking this rule may override it. Preserve historical artifacts.
- Still images, render contact sheets, technical reports, tests, datasets and
  executable release archives remain in scope. Do not make technical packaging
  depend on new videos or presentations.
- Use uniform release tags `apollo-vMAJOR.MINOR.PATCH` and display names
  `Apollo vMAJOR.MINOR.PATCH — Short Descriptive Name`. See `docs/RELEASES.md`.
- Commit meaningful completed checkpoints periodically and push at completion.

## Codebase navigation

- At the beginning of each coding task, consult `FILEMAP.md` to locate relevant files and understand their responsibilities.
- Treat the map as a navigation aid, not as authoritative source code. Verify behavior by inspecting the relevant implementation.
- Prefer targeted exploration over reading the entire repository when the map identifies the relevant area.
- If `FILEMAP.md` is missing or inaccurate, inspect the repository and create or correct it.

## Keep the file map current

- After changes, update `FILEMAP.md` when an important file is added, removed, renamed, moved, or changes responsibility.
- Update affected entries and relationships only; avoid rewriting unrelated sections.
- Do not update the map for minor internal edits that leave file responsibilities unchanged.
- Do not list generated files, dependencies, caches, or build artifacts.
- Keep the map concise (aim for 100–200 lines or fewer), accurate, and useful for locating code.
- Before finishing a task, check whether the map needs updating.

## Existing project conventions

- Preserve existing architecture, coding conventions, and unrelated project instructions.
- Do not modify application behavior solely to make the map match; fix the map instead.
