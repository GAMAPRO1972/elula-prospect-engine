# AI Development Guide

## Purpose

This guide defines how AI assistants should work on Elula Prospect Engine. The authoritative onboarding document remains [Project Context](PROJECT_CONTEXT.md).

## Responsibilities

Gary:

- CEO and Product Owner.
- Defines commercial priorities.
- Approves live sync, releases, tags, pushes, and production changes.

ChatGPT:

- Chief Software Architect.
- Owns architecture direction, roadmap, documentation, release planning, and code review.
- Explains tradeoffs and keeps work aligned with the business objective.

Codex:

- Senior Software Engineer.
- Implements scoped changes.
- Refactors safely.
- Runs validation.
- Reports changed files, test results, and operational risks.

## Development Lifecycle

This lifecycle is mandatory for every future sprint unless Gary explicitly approves an exception.

```text
Sprint Planning
↓
Architecture Review
↓
Implementation
↓
Compile
↓
Dry Run
↓
Limited Live Validation
↓
Documentation Update
↓
Release
↓
Git Tag
↓
Project Context Update
↓
Next Sprint
```

## Development Workflow

1. Read the user request and relevant docs.
2. Inspect the current repository state.
3. Read affected files before editing.
4. Keep changes scoped.
5. Preserve existing CLI behavior unless explicitly changed.
6. Provide complete replacement files when files are changed.
7. Avoid temporary hacks.
8. Report exactly what changed.

## Validation Workflow

For code changes, run:

```powershell
.venv\Scripts\python.exe -m compileall commands config integrations modules tools
```

For workflow validation, prefer:

```powershell
.venv\Scripts\python.exe main.py execute --limit 3 --dry-run
```

For intelligence report validation, use:

```powershell
.venv\Scripts\python.exe main.py execute --limit 3 --intelligence --dry-run
```

Only run limited live sync when explicitly approved:

```powershell
.venv\Scripts\python.exe main.py execute --limit 3
```

Never run full live sync unless explicitly instructed.

## Documentation Workflow

When documentation changes:

- keep `PROJECT_CONTEXT.md` authoritative;
- avoid duplicating long explanations across documents;
- update README links when new core docs are added;
- clearly mark implemented, planned, and future work;
- keep wording concise and operational;
- use Elula BizHub terminology in user-facing documentation.

## Release Workflow

Do not release unless explicitly instructed.

When approved:

1. Run `git status`.
2. Confirm changed files.
3. Run compile validation.
4. Run dry-run validation.
5. Run limited live validation only if approved.
6. Update release docs.
7. Commit approved files.
8. Create the tag.
9. Push branch and tag.
10. Create ZIP backup.

## Definition of Done

A task is done when:

- requested files are created or updated;
- application behavior is preserved unless explicitly changed;
- safety controls are preserved;
- validation has run or a clear reason is reported;
- no unauthorized commit, tag, push, or live sync occurred;
- final report lists changed files, created files, validation results, and risks.

A sprint is not complete until:

- code is validated;
- documentation is updated;
- `PROJECT_CONTEXT.md` is current;
- `CHANGELOG.md` is updated;
- `RELEASES.md` is updated;
- Git is tagged;
- GitHub is current.

## Rules for Modifying Production Code

- Never use temporary hacks.
- Preserve `--limit`.
- Preserve `--dry-run`.
- Do not bypass import history.
- Do not add external APIs without an approved provider design.
- Do not write new intelligence into Elula BizHub without approved mapping.
- Do not write Google Business Profile intelligence into Elula BizHub until explicitly approved.
- Keep modules loosely coupled.
- Prefer provider interfaces for future integrations.

## Rules for Dry-Run Validation

- Dry-run must not create or update Elula BizHub contacts.
- Dry-run must not create opportunities.
- Dry-run must not create tasks.
- Dry-run must not write import history.
- Dry-run may still create local reports, output files, and archive processed input CSV files.
- Dry-run should show what would have happened.
- Dry-run should be used before any live sync test.

## Rules for Documentation Updates

- Update docs when architecture, workflow, release status, or safety rules change.
- Keep documentation commercial and practical.
- Avoid claiming planned features are implemented.
- Keep `PROJECT_CONTEXT.md` as the first document future engineers and AI assistants should read.
