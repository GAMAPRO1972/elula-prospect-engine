# Product Backlog

```text
Current Version: v0.5.0
Working Release: v0.5.1 Sales Readiness
Last Updated: 2026-07-04
Purpose: Operational backlog for Elula Prospect Engine sales readiness.
```

## Operational Readiness Summary

The system is operationally close to ready for generating and preparing 50 security company prospects, provided the run uses the approved safety sequence:

1. Confirm Docker Desktop is running and accessible.
2. Run discovery or place a verified scraper CSV in `input/`.
3. Run dry-run validation with `--limit 3`.
4. Run intelligence report generation with a controlled limit.
5. Perform limited live sync only when explicitly approved.

Current local data is sufficient for report review and sales preparation:

- `output/results_processed.csv` contains 352 processed security prospects.
- The first 50 processed prospects contain 49 phone numbers.
- The first 50 processed prospects contain 36 websites.
- All 352 processed prospects contain public review rating data.
- All 352 processed prospects contain opening-hours data.

Operational caution:

- `input/` is currently empty, so the normal processing command has no queued CSV to process.
- A fresh end-to-end discovery run depends on Docker Desktop and scraper output.
- Docker is installed, but the Docker daemon was not accessible during this review.
- `tags.json` is empty; this is not blocking while the security campaign has no configured tags, but it can block future campaigns that require tags.

## Completed Features

### Prospect Discovery

- Google Maps scraper workflow.
- Campaign keyword export to scraper query file.
- Campaign-based discovery structure by industry and region.
- Security Gauteng campaign configuration.

### Prospect Processing

- CSV input detection from `input/`.
- Lead cleaning.
- Standard prospect record generation.
- Phone, website, address, rating, review count, opening-hours, and business-status capture.
- Within-run deduplication.
- Opportunity scoring.
- Owner assignment.
- Primary and secondary product assignment.
- Processed CSV export to `output/`.
- Source CSV archival to `archive/`.

### Elula BizHub Sync

- GoHighLevel / Elula BizHub API client.
- Contact lookup and upsert.
- Opportunity creation.
- Initial follow-up task creation.
- Pipeline, stage, owner, and tag metadata resolution.
- Persistent import history ledger.
- Cross-run duplicate prevention.
- Dry-run mode that prevents CRM writes and import-history writes.
- Safe `--limit` workflow for controlled validation.
- Metadata refresh command.

### Intelligence and Reporting

- People enrichment service foundation.
- Website intelligence service foundation.
- Google Business Profile parser and intelligence model.
- Business intelligence CSV report.
- Business intelligence XLSX report.
- Sales Opportunity Engine.
- Elula Business Growth Assessment PDF reports.
- Executive assessment report redesign for v0.5.1 Sales Readiness.

### Documentation and Operating Controls

- Project context.
- Roadmap.
- Changelog.
- Testing guidance.
- Deployment guidance.
- Engineering decisions.
- AI development guide.
- Release process.
- Operational safety rules for dry-run, limited live sync, and production sync.

## P1 Release Blockers

### P1-001: Confirm Docker Desktop Access Before Monday Discovery

Status: open.

Operational impact:

- Fresh prospect discovery may fail if Docker Desktop is not running or the local user cannot access the Docker daemon.

Evidence:

- Docker CLI is installed.
- Docker daemon access failed during review with a permission or daemon access error.

Required action:

- Start Docker Desktop and confirm `docker info` succeeds before running `main.py execute`.

### P1-002: Refresh or Confirm Elula BizHub Metadata Before Live Sync

Status: open.

Operational impact:

- Incorrect or stale metadata can route prospects to the wrong pipeline, stage, owner, or tags.

Evidence:

- Security Prospecting pipeline is present locally.
- Gary owner metadata is present locally.
- Security stages are present locally.
- Metadata was last refreshed on 2026-07-02.

Required action:

- Before any live sync, refresh metadata or manually confirm that Security Prospecting, New Prospect, Gary, and required tags still exist in Elula BizHub.

### P1-003: Run Limited Dry-Run Validation Before Any Live Sync

Status: open.

Operational impact:

- Live CRM writes can create contacts, opportunities, and tasks. A dry-run is required to validate routing, counts, and failures before production activity.

Evidence:

- Security Gauteng has `sync_to_ghl` set to `true`.
- Running `execute` without `--dry-run` can perform live CRM writes.

Required action:

- Use `--dry-run --limit 3` before live sync.
- Use limited live sync only when explicitly approved.

### P1-004: Confirm Input Source for the 50-Prospect Batch

Status: open.

Operational impact:

- `process` and `execute` operate on CSV files in `input/`; if no CSV exists and scraper fails, no new prospects will be processed.

Evidence:

- `input/` currently has 0 CSV files.
- Existing processed output has 352 records, but it is not the normal input queue.

Required action:

- Either run successful discovery to create `input/results.csv` or intentionally place a validated source CSV in `input/`.

## P2 Sales Enablers

### P2-001: 50-Prospect Sales Batch Operating Checklist

Status: backlog.

Value:

- Reduces Monday execution risk by giving the operator a repeatable checklist for scrape, dry-run, report generation, live sync approval, and sales handoff.

### P2-002: Sales Handoff Pack

Status: backlog.

Value:

- Package the 50 selected companies, contact details, business assessment PDFs, top findings, and call priorities into a single sales-ready folder or spreadsheet.

### P2-003: Report Index CSV

Status: backlog.

Value:

- Create an operator-friendly index linking each company to its generated PDF report, score, top opportunity, phone number, website, and assigned owner.

### P2-004: Discovery Meeting Agenda Export

Status: backlog.

Value:

- Convert report discussion questions into a structured call agenda for sales follow-up.

### P2-005: Pre-Sync Review Sheet

Status: backlog.

Value:

- Provide a review stage where the operator can approve or exclude prospects before CRM sync.

## P3 Product Enhancements

### P3-001: Safer 50-Record Batch Command

Status: backlog.

Value:

- Add a controlled command that selects, validates, reports, and prepares exactly 50 prospects without relying on manual file movement.

### P3-002: Input File Preview and Confirmation

Status: backlog.

Value:

- Show file name, row count, campaign, and sync mode before processing starts.

### P3-003: Dry-Run Report Persistence

Status: backlog.

Value:

- Save dry-run summaries as timestamped operational reports for audit and Monday sales review.

### P3-004: Tag Metadata Guardrail

Status: backlog.

Value:

- Warn clearly when tag metadata is empty and the selected campaign expects tags.

### P3-005: Discovery Dependency Check

Status: backlog.

Value:

- Add a preflight check for Docker availability, Docker daemon access, query file existence, and output directory permissions.

### P3-006: Report Generation From Processed Output

Status: backlog.

Value:

- Allow controlled report generation from an existing processed CSV without requiring a raw input CSV to be reprocessed.

### P3-007: Import History Review Utility

Status: backlog.

Value:

- Let operators check whether a planned batch contains previously imported prospects before approving live sync.

## P4 Future Ideas

### P4-001: Decision Maker Discovery

Status: planned for v0.6.0.

Value:

- Attach real decision makers to imported businesses using approved enrichment providers, confidence scoring, and source tracking.

### P4-002: AI Call Preparation Briefs

Status: future.

Value:

- Generate concise call briefs with business context, likely pain points, positioning, and discovery questions.

### P4-003: AI Outreach Drafting

Status: future.

Value:

- Generate controlled WhatsApp and email drafts for approved campaigns with operator review.

### P4-004: Appointment Outcome Tracking

Status: future.

Value:

- Connect prospect source, report findings, owner activity, and booked appointments into measurable sales performance reporting.

### P4-005: Campaign Quality Dashboard

Status: future.

Value:

- Compare industries, regions, lead sources, contact availability, report scores, sync results, and appointment conversion.

### P4-006: Release Packaging and Backup Automation

Status: future.

Value:

- Standardise tagged releases, ZIP backups, and rollback-ready release assets.

## Operational Review Notes

### Prospect Discovery

- Campaign query export is simple and campaign-driven.
- Fresh discovery depends on Docker Desktop and the Google Maps scraper image.
- If scraper fails but existing local CSV files exist in `input/`, the workflow continues safely.
- If scraper fails and `input/` is empty, the workflow exits without processing.

### Processing

- Processing converts raw scraper rows into standard prospect records.
- Deduplication runs within the current file.
- Processed source files are archived immediately after processing.
- Operators should not place unreviewed files in `input/` because every CSV there will be processed.

### Intelligence Reports

- Intelligence report generation is report-only.
- Google Business intelligence is not written into Elula BizHub.
- Client PDFs are generated locally in `reports/client_reports/`.
- Existing processed data is sufficient for generating sales review reports.

### Elula BizHub Sync

- Live sync is controlled by campaign configuration and command flags.
- Security Gauteng is configured with `sync_to_ghl: true`.
- Dry-run protects Elula BizHub writes and import-history writes.
- Import history prevents repeat imports across live runs.
- Owner and pipeline metadata resolve correctly from local metadata for the security campaign.

## Monday Sales Activity Risks

1. Docker daemon access may block fresh prospect discovery.
2. `input/` is empty, so no new processing will happen unless discovery succeeds or a CSV is placed there.
3. Running `execute` without `--dry-run` can perform live CRM writes because the security campaign has sync enabled.
4. Metadata should be refreshed or confirmed before live sync to prevent routing issues.
5. Empty `tags.json` is safe for the current security campaign because no tags are configured, but it is a future campaign risk.
6. Existing processed data is available for a 50-prospect sales batch, but it should be treated as a prepared output source rather than the normal processing queue.
