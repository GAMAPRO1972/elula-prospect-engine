# Project Context

## Current Version

`v0.4.0`

Elula Prospect Engine is a Python CLI application for campaign-based prospect discovery, enrichment, scoring, duplicate prevention, and controlled sync into Elula BizHub.

## Project Vision

Build a reliable prospecting engine that turns business discovery data into qualified appointment opportunities for Elula Business Dynamics.

The long-term vision is a sales intelligence platform that can discover companies, understand their digital footprint, identify relevant decision makers, prepare call intelligence, support AI-assisted outreach, and centralize the resulting sales pipeline inside Elula BizHub.

## Business Objective

Generate qualified appointments for Elula Business Dynamics.

The system supports this by:

- discovering target businesses from campaign search terms;
- cleaning and deduplicating lead data;
- scoring opportunity quality;
- assigning owners and product focus;
- enriching prospects with people and website intelligence frameworks;
- importing qualified prospects into Elula BizHub;
- preventing duplicate contacts, opportunities, and tasks across repeated runs.

Appointments are the primary KPI. All engineering decisions should improve appointment quality, lead routing clarity, operational reliability, or sales execution speed.

## High-Level Architecture

```text
Campaign Config
      |
      v
Google Maps Scraper
      |
      v
Raw CSV Input
      |
      v
Lead Processing
  - cleaning
  - deduplication
  - scoring
  - assignment
      |
      v
Pre-Sync Intelligence
  - people enrichment framework
  - website intelligence framework
  - import history duplicate check
      |
      v
Elula BizHub Sync
  - contact upsert
  - opportunity creation
  - task creation
      |
      v
Sales Follow-Up
```

## Folder Structure

```text
campaigns/           Campaign definitions and search query files.
commands/            CLI command modules.
config/              Settings, product rules, and configuration logic.
data/                Persistent runtime data such as import history.
docs/                Permanent engineering documentation.
integrations/ghl/    Elula BizHub API integration and metadata.
integrations/people/ People enrichment provider foundation.
integrations/website/ Website intelligence analysis foundation.
modules/             Core processing, sync, enrichment, and utility logic.
tools/               Operational scripts and support utilities.
input/               Incoming CSV files waiting for processing.
output/              Processed prospect exports.
archive/             Archived source files after processing.
logs/                Runtime and sync logs.
reports/             Operational reports.
scraper-data/        Scraper runtime data.
templates/           Reusable templates.
```

## Current Modules

- `main.py` defines the CLI entry point.
- `commands/run.py` exports campaign queries and starts the scraper.
- `commands/process.py` processes CSV input and optionally syncs prospects.
- `commands/execute.py` runs the full workflow.
- `commands/refresh_ghl_metadata.py` refreshes Elula BizHub metadata.
- `modules/campaign_manager.py` loads campaign configuration.
- `modules/process_leads.py` builds processed prospects.
- `modules/cleaner.py` cleans raw scraper records.
- `modules/deduplicator.py` removes duplicates within a processing run.
- `modules/opportunity_scoring.py` scores prospects.
- `modules/assignment_engine.py` assigns owner and product focus.
- `modules/import_history.py` stores cross-run import history.
- `modules/ghl_sync.py` orchestrates Elula BizHub sync.
- `integrations/people/*` defines the people enrichment foundation.
- `integrations/website/*` defines the website intelligence foundation.
- `integrations/ghl/*` handles Elula BizHub API operations.

## Completed Features

- Google Maps campaign scraper.
- Campaign manager.
- Lead cleaning.
- Deduplication.
- Opportunity scoring.
- Product assignment.
- Owner assignment.
- Elula BizHub integration.
- Contact upsert.
- Opportunity creation.
- Task creation.
- Metadata refresh.
- Persistent import history.
- Cross-run duplicate prevention.
- People enrichment framework.
- Website intelligence framework.
- Dry-run mode.
- Safe `--limit` testing.
- README and AGENTS instructions.

## Development Workflow

1. Inspect the current repository state.
2. Read the relevant modules before editing.
3. Keep changes scoped to the requested sprint or fix.
4. Provide complete replacement files when files are changed.
5. Compile before completion for code changes.
6. Use `--dry-run` before live sync tests.
7. Use `--limit` before any larger live run.
8. Do not commit unless explicitly instructed.

## Testing Workflow

Standard compile check:

```powershell
.venv\Scripts\python.exe -m compileall commands config integrations modules tools
```

Safe execution check:

```powershell
.venv\Scripts\python.exe main.py execute --limit 3 --dry-run
```

Limited live check, only when approved:

```powershell
.venv\Scripts\python.exe main.py execute --limit 3
```

Never run full live sync unless explicitly instructed.

## Git Workflow

- Use `git status` before release work.
- Do not commit unless explicitly instructed.
- Do not create tags unless explicitly instructed.
- Do not push unless explicitly instructed.
- Keep unrelated changes separate.
- Never revert user changes without explicit approval.

## Release Workflow

When explicitly instructed:

1. Run `git status`.
2. Confirm only approved files changed.
3. Run compile checks.
4. Run dry-run validation.
5. Run limited live validation only if approved.
6. Commit approved changes.
7. Create the release tag.
8. Push branch and tag.
9. Create ZIP backup.

## Sprint History

- `v0.1`: Initial prospecting engine foundation.
- `v0.2`: Campaign processing, cleaning, scoring, and assignment improvements.
- `v0.3`: Elula BizHub sync, metadata refresh, and controlled `--limit` testing.
- `v0.4`: Import history, cross-run duplicate prevention, people enrichment foundation, website intelligence foundation, and dry-run mode.

## Current Roadmap

- `v0.5`: Google Business Profile Intelligence.
- `v0.6`: Decision Maker Discovery.
- `v0.7`: AI Call Preparation.
- `v0.8`: AI Outreach.
- `v0.9`: Sales Intelligence Platform.
- `v1.0`: Commercial Release.

## Current Project Status

The `v0.4.0` application code is complete. The system has production-safety foundations for duplicate prevention, dry-run execution, people enrichment, and website intelligence. People and website intelligence are not yet written into Elula BizHub.

## Immediate Next Task

Prepare for `v0.5`: Google Business Profile Intelligence. The next implementation should add safe collection and interpretation of Google business profile signals without disrupting existing sync behavior.

## AI Team Roles

- Gary: CEO and Product Owner.
- ChatGPT: Chief Software Architect for architecture, roadmap, documentation, release management, and code reviews.
- Codex: Senior Software Engineer for implementation, refactoring, and testing.

## Coding Rules

- Never use temporary hacks.
- Provide complete replacement files when files are changed.
- Preserve CLI behavior unless the task explicitly changes it.
- Preserve `--limit` behavior.
- Use `--dry-run` before live sync.
- Do not commit unless explicitly instructed.
- Keep modules loosely coupled.
- Prefer provider interfaces for future external services.
- Keep production safety higher priority than cleverness.

## Business Rules

- Appointments are the primary KPI.
- Elula BizHub is the central CRM and operations platform.
- Avoid unnecessary subaccount fragmentation.
- Duplicate prevention is mandatory before live CRM writes.
- Live sync must be controlled, logged, and limited before scale.
- Sales intelligence must support practical call preparation and appointment generation.

## Future Vision

The Prospect Engine should become a centralized sales intelligence and appointment-generation platform for Elula Business Dynamics. Future versions should add deeper business profile intelligence, decision-maker discovery, AI-assisted call prep, AI outreach support, and reporting dashboards that connect lead source quality to appointment outcomes.
