# Elula Prospect Engine

Current version: `v0.4.0`

Elula Prospect Engine is a Python CLI application that discovers businesses, processes prospect data, enriches records, prevents duplicate imports, and syncs qualified prospects into Elula BizHub.

Elula BizHub is Elula Business Dynamics' branded GoHighLevel platform. Business documentation should use Elula BizHub terminology, except where direct API naming is required.

## Business Objective

The primary objective is to generate qualified appointments for Elula Business Dynamics.

The Prospect Engine supports centralized lead generation by turning Google Maps campaign data into scored, assigned, CRM-ready prospects with supporting sales intelligence.

## Implemented in v0.4.0

- Google Maps campaign scraper.
- Campaign manager.
- Lead cleaning.
- Deduplication.
- Opportunity scoring.
- Product assignment.
- Owner assignment.
- Elula BizHub contact upsert.
- Opportunity creation.
- Task creation.
- Metadata refresh.
- Persistent import history.
- Cross-run duplicate prevention.
- People enrichment framework.
- Website intelligence framework.
- Dry-run mode.
- Safe `--limit` testing.

## Documentation

The permanent engineering reference is stored in `docs/`.

- [Project Context](docs/PROJECT_CONTEXT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Changelog](docs/CHANGELOG.md)
- [Releases](docs/RELEASES.md)
- [Business Objectives](docs/BUSINESS_OBJECTIVES.md)
- [Coding Standards](docs/CODING_STANDARDS.md)
- [Testing](docs/TESTING.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Engineering Decisions](docs/DECISIONS.md)

Start with [Project Context](docs/PROJECT_CONTEXT.md) when onboarding a new engineer or AI assistant.

## Folder Structure

```text
campaigns/          Campaign definitions and search query files.
commands/           CLI command modules.
config/             Settings, product rules, and configuration logic.
data/               Persistent runtime data such as import history.
docs/               Permanent engineering documentation.
integrations/ghl/   Elula BizHub API integration files and metadata.
integrations/people/ People enrichment framework.
integrations/website/ Website intelligence framework.
modules/            Core processing, enrichment, sync, and utility logic.
tools/              Operational utilities and support tooling.
input/              Incoming CSV files waiting for processing.
output/             Processed prospect exports.
archive/            Archived source files after processing.
logs/               Runtime and sync logs.
reports/            Operational reports.
scraper-data/       Google Maps scraper data.
templates/          Reusable templates.
```

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Update `.env` with approved local or production credentials. Never commit real credentials.

## Core Commands

Process existing CSV input:

```powershell
.venv\Scripts\python.exe main.py process --industry security --campaign gauteng
```

Run scraper only:

```powershell
.venv\Scripts\python.exe main.py run --industry security --campaign gauteng
```

Run full workflow safely without Elula BizHub writes:

```powershell
.venv\Scripts\python.exe main.py execute --industry security --campaign gauteng --limit 3 --dry-run
```

Run limited live sync only after validation:

```powershell
.venv\Scripts\python.exe main.py execute --industry security --campaign gauteng --limit 3
```

Refresh Elula BizHub metadata:

```powershell
.venv\Scripts\python.exe main.py refresh-ghl-metadata --pipeline "Security Prospecting"
```

## Safety Rules

- Use `--dry-run` before live sync.
- Use `--limit` before any larger live run.
- Never run a full live sync unless explicitly instructed.
- Do not commit unless explicitly instructed.
- Do not place secrets in documentation, commits, logs, or examples.

## Compile Check

Run before completing engineering work:

```powershell
.venv\Scripts\python.exe -m compileall commands config integrations modules tools
```

## Release

Release instructions are documented in [Deployment](docs/DEPLOYMENT.md) and [Releases](docs/RELEASES.md). Do not commit, tag, push, or package a release unless explicitly instructed.
