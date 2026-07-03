# Project Context

```text
Current Version: v0.4.0
Status: Production Beta
Last Updated: 2026-07-03
Repository: https://github.com/GAMAPRO1972/elula-prospect-engine
Next Objective: Sprint 5 - Google Business Profile Intelligence
```

This is the first document to read for all future developers, AI assistants, sprint handoffs, and project onboarding. It is the authoritative context document for the Elula Prospect Engine.

## First Page Summary

What are we building?

Elula Prospect Engine is a Python CLI application that discovers businesses, processes prospect data, prepares sales intelligence, prevents duplicate imports, and syncs qualified prospects into Elula BizHub.

Why are we building it?

Elula Business Dynamics needs a repeatable system for generating qualified appointments. The Prospect Engine creates the upstream lead generation and intelligence layer for that appointment engine.

What problem does it solve?

Manual prospecting is slow, inconsistent, difficult to measure, and prone to duplicate CRM activity. The Prospect Engine centralizes prospect discovery, cleaning, scoring, owner assignment, enrichment checks, duplicate prevention, and controlled Elula BizHub sync.

Current version:

`v0.4.0`

Current project status:

The `v0.4.0` application code is complete. It includes production-safety foundations: dry-run mode, safe `--limit` testing, persistent import history, cross-run duplicate prevention, people enrichment foundation, and website intelligence foundation.

Immediate next task:

Prepare `v0.5.0`: Google Business Profile Intelligence. The next implementation should add safe profile intelligence without changing existing live sync behavior until mapping and operational rules are approved.

## Business Objective

Generate qualified appointments for Elula Business Dynamics.

Appointments are the primary KPI. Lead volume is useful only when it improves the number or quality of qualified appointments.

## Product Vision

The Prospect Engine is the first layer of a broader Elula Business Dynamics platform:

- Prospect Engine discovers and qualifies business prospects.
- Sales Machine will manage outreach and follow-up execution.
- Industry Intelligence will provide sector-specific context and positioning.
- AI Assistants will support call preparation, outreach drafting, and operational workflows.
- Elula BizHub remains the central CRM and automation platform.

See [Product Vision](PRODUCT_VISION.md) for the long-term platform view.

## High-Level Architecture

```text
Google Maps Campaigns
        |
        v
Processing
  - cleaning
  - deduplication
  - scoring
  - assignment
        |
        v
Intelligence
  - people enrichment foundation
  - website intelligence foundation
  - future Google Business Profile Intelligence
        |
        v
Elula BizHub
  - contact upsert
  - opportunity creation
  - task creation
        |
        v
Sales Follow-Up
  - owner action
  - qualification
  - appointment generation
```

## Repository Structure

```text
campaigns/            Campaign definitions and search query files.
commands/             CLI command modules.
config/               Settings, product rules, and configuration logic.
data/                 Persistent runtime data such as import history.
docs/                 Permanent engineering documentation.
integrations/ghl/     Elula BizHub API integration and metadata.
integrations/people/  People enrichment provider foundation.
integrations/website/ Website intelligence analysis foundation.
modules/              Core processing, sync, enrichment, and utility logic.
tools/                Operational scripts and support utilities.
input/                Incoming CSV files waiting for processing.
output/               Processed prospect exports.
archive/              Archived source files after processing.
logs/                 Runtime and sync logs.
reports/              Operational reports.
scraper-data/         Scraper runtime data.
templates/            Reusable templates.
```

## Current Modules

- `main.py`: CLI entry point.
- `commands/run.py`: exports campaign queries and starts the scraper.
- `commands/process.py`: processes CSV input and optionally syncs prospects.
- `commands/execute.py`: runs the full workflow.
- `commands/refresh_ghl_metadata.py`: refreshes Elula BizHub metadata.
- `modules/campaign_manager.py`: loads campaign configuration.
- `modules/process_leads.py`: builds processed prospects.
- `modules/cleaner.py`: cleans raw scraper records.
- `modules/deduplicator.py`: removes duplicates within a processing run.
- `modules/opportunity_scoring.py`: scores prospects.
- `modules/assignment_engine.py`: assigns owner and product focus.
- `modules/import_history.py`: stores cross-run import history.
- `modules/ghl_sync.py`: orchestrates Elula BizHub sync.
- `integrations/ghl/*`: handles Elula BizHub API operations.
- `integrations/people/*`: provides the people enrichment foundation.
- `integrations/website/*`: provides the website intelligence foundation.

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

## Development Workflow

1. Review `README.md`, this document, and the relevant module files.
2. Inspect current repository status.
3. Keep changes scoped to the task.
4. Preserve existing CLI behavior unless explicitly changing it.
5. Provide complete replacement files when files are changed.
6. Compile before completion for code changes.
7. Use dry-run before live sync validation.
8. Do not commit, tag, or push unless explicitly instructed.

## Testing Workflow

Compile check:

```powershell
.venv\Scripts\python.exe -m compileall commands config integrations modules tools
```

Safe workflow validation:

```powershell
.venv\Scripts\python.exe main.py execute --limit 3 --dry-run
```

Limited live validation, only when approved:

```powershell
.venv\Scripts\python.exe main.py execute --limit 3
```

Never run full live sync unless explicitly instructed.

## Release Workflow

When explicitly instructed:

1. Run `git status`.
2. Confirm release scope and changed files.
3. Run compile validation.
4. Run dry-run validation.
5. Run limited live validation only if approved.
6. Update documentation.
7. Commit approved files.
8. Create the version tag.
9. Push branch and tag.
10. Create ZIP backup.

## AI Team Responsibilities

- Gary: CEO and Product Owner. Defines commercial priorities, approves live sync and release actions.
- ChatGPT: Chief Software Architect. Owns architecture direction, roadmap, documentation, release planning, and code review.
- Codex: Senior Software Engineer. Implements scoped changes, refactors safely, runs validation, and reports outcomes.

## Sprint History

- `v0.1 Foundation`: initial Google Maps prospecting foundation.
- `v0.2 Processing`: cleaning, deduplication, scoring, product assignment, and owner assignment.
- `v0.3 Elula BizHub Integration`: metadata refresh, contact upsert, opportunity creation, task creation, and safe `--limit` testing.
- `v0.4 Production Platform`: import history, cross-run duplicate prevention, people enrichment foundation, website intelligence foundation, dry-run mode, and engineering documentation.

## Business Rules

- Appointments are the primary KPI.
- Elula BizHub is the central CRM and operations platform.
- Duplicate prevention is mandatory before live CRM writes.
- Dry-run validation must precede live sync validation.
- Live sync must use `--limit` before scale.
- People and website intelligence must not write to Elula BizHub until mapping and operating rules are approved.

## Future Vision

The Prospect Engine should become the discovery and intelligence source for a broader Elula Business Dynamics platform. Future releases should add Google Business Profile Intelligence, decision-maker discovery, AI call preparation, AI outreach, reporting dashboards, and sales intelligence workflows that connect prospect quality to booked appointments.
