# Coding Standards

## Core Rules

- Never use temporary hacks.
- Always provide complete replacement files when files are changed.
- Do not commit unless explicitly instructed.
- Preserve existing CLI behavior unless the task explicitly changes it.
- Preserve `--limit` behavior.
- Use `--dry-run` before live sync validation.
- Keep production safety higher priority than cleverness.

## Python Standards

- Use clear module boundaries.
- Keep functions focused and testable.
- Prefer standard library functionality unless a dependency already exists and is appropriate.
- Avoid unnecessary dependencies.
- Use dataclasses for simple data models when they fit the existing project style.
- Keep comments useful and explain non-obvious business or safety logic.

## Architecture Standards

- Keep modules loosely coupled.
- Prefer provider interfaces for future external services.
- Keep enrichment frameworks separate from sync writes.
- Do not write new intelligence into Elula BizHub until field mapping and operational behavior are approved.
- Keep duplicate prevention close to the sync boundary.
- Keep dry-run behavior explicit and auditable.

## Elula BizHub Safety Standards

- Never run a full live sync unless explicitly instructed.
- Always run dry-run before live sync.
- Always run limited live sync before larger live sync.
- Validate metadata before live sync.
- Confirm pipeline, stage, owner, tags, and field mappings.
- Stop immediately if duplicates or incorrect routing appear.

## Documentation Standards

- Use Elula BizHub terminology in user-facing documentation.
- Use GoHighLevel naming only where API clarity requires it.
- Clearly distinguish implemented, planned, and future features.
- Keep documents suitable for both human engineers and future AI assistants.

## Release Standards

Before a release:

1. Confirm scope.
2. Run `git status`.
3. Run compile checks.
4. Run dry-run validation.
5. Run limited live validation only if approved.
6. Commit only approved files.
7. Tag only when instructed.
8. Push only when instructed.
9. Create ZIP backup when instructed.
