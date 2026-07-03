# Elula Prospect Engine

Current version: `v0.3.0`

## Project Overview

Elula Prospect Engine is a Python CLI application for prospecting campaigns. It scrapes Google Maps, processes raw prospect data, qualifies records, and syncs approved prospects into Elula BizHub.

Elula BizHub is Elula Business Dynamics' branded GoHighLevel platform. Use Elula BizHub terminology in business and operational documentation. Reference GoHighLevel only where API naming or technical integration clarity requires it.

## Business Objective

The objective of this project is to generate qualified appointments for Elula Business Dynamics.

The system supports a centralized outbound operation by turning campaign search terms into structured prospect records, CRM contacts, opportunities, tasks, and sales follow-up activity.

## Main Features

- Campaign-based Google Maps scraping.
- Industry and campaign-specific search query management.
- CSV prospect processing and enrichment.
- Product and campaign rule application.
- Elula BizHub contact, opportunity, owner, pipeline, stage, tag, and task integration.
- Metadata refresh from the live Elula BizHub API.
- Controlled live sync using record limits.
- Local output, archive, logs, reports, and operational support folders.

## Folder Structure

```text
campaigns/          Campaign definitions and search query files.
commands/           CLI command modules.
config/             Settings, product rules, and configuration logic.
integrations/ghl/   Elula BizHub API integration files and metadata.
modules/            Core prospecting, processing, sync, and utility logic.
tools/              Operational scripts, diagnostics, and support tools.
input/              Incoming CSV files waiting for processing.
output/             Processed prospect exports.
archive/            Archived source files after processing.
exports/            Exported data artifacts.
logs/               Runtime and sync logs.
reports/            Operational reports.
scraper-data/       Google Maps scraper data.
templates/          Reusable templates.
```

## Installation

1. Create and activate a Python virtual environment.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

3. Create a local `.env` file from `.env.example`.

```powershell
Copy-Item .env.example .env
```

4. Update `.env` with local development or approved production credentials.

Do not commit `.env` or any real API keys.

## .env Configuration

Required values are defined in `.env.example`.

```text
GOOGLE_MAPS_API_KEY=your_api_key_here
GHL_COMPANY_ID=your_company_id_here
NODE_ENV=development
```

Operational rules:

- Keep secrets in `.env` only.
- Do not place real credentials in documentation, commits, examples, logs, or exported files.
- Use approved Elula BizHub API credentials for live sync and metadata refresh.
- Confirm the target company, pipeline, stage, owner, tags, and custom field mappings before syncing records.

## Campaign Structure

Campaigns are organized by industry and campaign name.

Example:

```text
campaigns/
  security/
    gauteng.json
    gauteng.txt
```

The `.json` file defines campaign metadata and sync behavior, including:

- campaign ID and name
- industry
- province and country
- source
- primary and secondary products
- target Elula BizHub pipeline
- whether live sync is enabled
- active status

The `.txt` file contains Google Maps search queries for the campaign.

## Commands

Run commands from the repository root.

### process

Processes CSV files from `input/` into structured prospect exports.

```powershell
.venv\Scripts\python.exe main.py process --industry security --campaign gauteng
```

Default values:

- `--industry security`
- `--campaign gauteng`

### run

Exports campaign search queries and runs the Google Maps scraper.

```powershell
.venv\Scripts\python.exe main.py run --industry security --campaign gauteng
```

### execute

Runs the complete workflow:

1. Export campaign queries.
2. Run the Google Maps scraper.
3. Process results.
4. Sync to Elula BizHub if the campaign enables live sync.

```powershell
.venv\Scripts\python.exe main.py execute --industry security --campaign gauteng
```

### refresh-ghl-metadata

Refreshes local Elula BizHub metadata from the live GoHighLevel API.

```powershell
.venv\Scripts\python.exe main.py refresh-ghl-metadata --pipeline "Security Prospecting"
```

Optional company override:

```powershell
.venv\Scripts\python.exe main.py refresh-ghl-metadata --pipeline "Security Prospecting" --company-id your_company_id_here
```

Updated metadata files:

- `integrations/ghl/pipelines.json`
- `integrations/ghl/stages.json`
- `integrations/ghl/owners.json`

## Safe Live Sync

Use `--limit` when running live sync through `execute`.

```powershell
.venv\Scripts\python.exe main.py execute --industry security --campaign gauteng --limit 5
```

Operational rules:

- Always run a limited live sync before any larger sync.
- Validate contacts, opportunities, tasks, owners, tags, pipeline, stages, and custom fields in Elula BizHub.
- Never run a full live sync unless explicitly instructed.
- Stop immediately if duplicates, incorrect routing, missing fields, wrong owners, or incorrect pipeline placement are detected.

## Elula BizHub Integration

The Elula BizHub integration is stored under `integrations/ghl/`.

Key integration files include:

- `api.py` - live API communication.
- `importer.py` - contact and import orchestration.
- `metadata.py` - pipeline, stage, and owner metadata refresh.
- `opportunities.py` - opportunity creation and updates.
- `tasks.py` - follow-up task handling.
- `field_mapping.json` - local-to-Elula BizHub field mapping.
- `custom_fields.json` - custom field metadata.
- `pipelines.json` - local pipeline metadata.
- `stages.json` - local stage metadata.
- `owners.json` - local owner metadata.
- `tags.json` - tag metadata.

Use refreshed metadata before production sync changes so CRM routing remains accurate.

## Testing Commands

Run this before completion:

```powershell
.venv\Scripts\python.exe -m compileall commands config integrations modules tools
```

Recommended operational checks:

```powershell
.venv\Scripts\python.exe main.py process --industry security --campaign gauteng
.venv\Scripts\python.exe main.py refresh-ghl-metadata --pipeline "Security Prospecting"
.venv\Scripts\python.exe main.py execute --industry security --campaign gauteng --limit 5
```

Only run live commands when credentials, campaign config, and sync targets have been checked.

## Release Process

Do not release unless explicitly instructed.

Release sequence:

1. Run `git status`.
2. Confirm only approved files changed.
3. Run the compile test.
4. Commit the approved changes.
5. Create the release tag.
6. Push the branch.
7. Push the tag.
8. Create a ZIP backup of the release state.

Example release commands:

```powershell
git status
.venv\Scripts\python.exe -m compileall commands config integrations modules tools
git add README.md
git commit -m "Release v0.3.0"
git tag v0.3.0
git push
git push origin v0.3.0
```

Create the ZIP backup after the release state is confirmed.

## Roadmap to v0.4.0

Planned priorities:

- Stronger duplicate detection before Elula BizHub sync.
- Clearer pre-sync validation reports.
- Campaign-level sync dry-run mode.
- Improved appointment qualification scoring.
- Better owner assignment and routing controls.
- Expanded operational reporting for processed, synced, failed, and skipped prospects.
- Safer release packaging and backup automation.
- More complete campaign templates for repeatable industry rollouts.
