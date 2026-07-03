# AGENTS.md

## Project Objective

Elula Prospect Engine exists to generate qualified appointments for Elula Business Dynamics. All changes must support reliable lead sourcing, enrichment, qualification, CRM sync, and appointment generation.

Elula BizHub is the branded GoHighLevel platform used for CRM, automations, communications, pipeline management, and lead operations.

## Agent Rules

- Provide complete replacement files only when delivering code. Do not provide partial snippets.
- Do not introduce temporary hacks, brittle shortcuts, or one-off fixes.
- Do not commit changes unless explicitly instructed.
- Keep implementations simple, maintainable, and production-ready.
- Preserve existing naming conventions, folder structure, and operational intent.
- Prefer reusable logic over duplicated campaign-specific code.
- Treat live CRM sync operations as controlled production actions.

## Current Architecture

- `campaigns` - campaign-specific inputs, outputs, and operational data.
- `commands` - executable command modules and workflow entry points.
- `config` - configuration, settings, constants, and environment-driven behavior.
- `integrations/ghl` - GoHighLevel / Elula BizHub integration logic.
- `modules` - core business logic, enrichment, processing, and reusable services.
- `tools` - operational utilities, scripts, diagnostics, and support tooling.

## Testing Requirements

Before completion, run:

```powershell
.venv\Scripts\python.exe -m compileall commands config integrations modules tools
```

Live sync rules:

- Run a limited live sync before any full sync.
- Never run a full live sync unless explicitly instructed.
- Validate record counts, target pipeline, tags, and field mappings before increasing sync volume.
- Stop immediately if duplicate creation, incorrect routing, or malformed CRM data is detected.

## Release Process

When explicitly instructed to release:

1. Run `git status`.
2. Commit the approved changes.
3. Create a release tag.
4. Push the branch and tag.
5. Create a ZIP backup of the release state.

Do not perform release actions unless explicitly instructed.
