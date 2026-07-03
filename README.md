# Elula Prospect Engine

## Vision

Elula Prospect Engine is the prospect discovery and intelligence layer for Elula Business Dynamics. Its long-term role is to feed qualified, sales-ready opportunities into Elula BizHub and support future sales automation, industry intelligence, and AI-assisted execution.

Current version: `v0.4.0`

## Current Status

`v0.4.0` is complete. The application code includes campaign scraping, lead processing, Elula BizHub sync, import history, cross-run duplicate prevention, people enrichment foundation, website intelligence foundation, dry-run mode, and safe `--limit` testing.

The next planned release is `v0.5.0`: Google Business Profile Intelligence.

For full onboarding context, start with [Project Context](docs/PROJECT_CONTEXT.md).

## Business Objective

Generate qualified appointments for Elula Business Dynamics.

The Prospect Engine discovers businesses, processes prospect data, prepares sales intelligence, prevents duplicate imports, and syncs qualified prospects into Elula BizHub.

## Related Projects

- Elula Prospect Engine: implemented prospect discovery, processing, enrichment foundation, and controlled Elula BizHub sync.
- Elula Sales Machine: planned sales execution layer for outreach, follow-up, appointment workflows, and sales operating rhythm.
- Industry Intelligence: planned intelligence layer for industry-specific insights, campaign strategy, qualification signals, and positioning.
- AI Assistants: planned AI layer for call preparation, outreach support, research summaries, and operational assistance.

## Documentation

The permanent engineering reference is stored in `docs/`.

- [Project Context](docs/PROJECT_CONTEXT.md)
- [Product Vision](docs/PRODUCT_VISION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Changelog](docs/CHANGELOG.md)
- [Releases](docs/RELEASES.md)
- [Business Objectives](docs/BUSINESS_OBJECTIVES.md)
- [Coding Standards](docs/CODING_STANDARDS.md)
- [Testing](docs/TESTING.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Engineering Decisions](docs/DECISIONS.md)
- [AI Development Guide](docs/AI_DEVELOPMENT_GUIDE.md)

## Core Commands

Safe full workflow validation:

```powershell
.venv\Scripts\python.exe main.py execute --industry security --campaign gauteng --limit 3 --dry-run
```

Limited live sync only after validation:

```powershell
.venv\Scripts\python.exe main.py execute --industry security --campaign gauteng --limit 3
```

Compile check:

```powershell
.venv\Scripts\python.exe -m compileall commands config integrations modules tools
```

## Safety Rules

- Use `--dry-run` before live sync.
- Use `--limit` before any larger live run.
- Never run a full live sync unless explicitly instructed.
- Do not commit, tag, or push unless explicitly instructed.
- Do not place secrets in documentation, commits, logs, or examples.
