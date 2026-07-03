# Changelog

## v0.5.0

Status: implemented locally, pending release commit and tag.

Released scope:

- Added Google Business Profile Intelligence foundation.
- Added local parser and client boundary for Google Business Profile-like data.
- Added Business Intelligence module.
- Added Sales Opportunity Engine.
- Added internal CSV and XLSX intelligence reports.
- Added branded Elula Business Growth Assessment PDF reports.
- Added `--intelligence` CLI option for report generation.
- Preserved dry-run and no-live-sync safety rules.
- Clarified execute workflow reporting so scraper failure is not reported as full workflow success.
- Removed stale duplicate execute command file.
- Documented that dry-run prevents Elula BizHub and import-history writes but may still create local processing outputs and archives.

Operational impact:

- Operators can generate report-only sales intelligence without writing Google Business intelligence to Elula BizHub.
- Reports identify conservative sales opportunities based on available public information.

## v0.4.0

Status: released. Sprint 4 is complete.

Released scope:

- Added persistent import history.
- Added cross-run duplicate prevention.
- Added people enrichment framework.
- Added website intelligence framework.
- Added dry-run mode.
- Preserved safe `--limit` testing.
- Improved sync summary counters.
- Added engineering documentation package.

Operational impact:

- Repeated runs can avoid duplicate Elula BizHub contacts, opportunities, and tasks.
- Engineers can run full workflow validation using `--dry-run` without live CRM writes.
- Future enrichment providers can be added without rewriting the sync core.

## v0.3.0

Released scope:

- Converted project documentation to reflect Python CLI application behavior.
- Documented Elula BizHub as the branded CRM platform.
- Added commands for `process`, `run`, `execute`, and `refresh-ghl-metadata`.
- Added safe limited live sync guidance using `--limit`.
- Added release process documentation.

Operational impact:

- The Prospect Engine became easier to operate as a controlled CLI workflow.
- Live sync testing became safer through explicit limits.

## v0.2.0

Released scope:

- Improved campaign processing structure.
- Added or refined lead cleaning.
- Added deduplication within processing runs.
- Added opportunity scoring.
- Added product and owner assignment foundations.

Operational impact:

- Raw scraper records could be converted into more useful prospect records.
- Campaign outputs became more consistent for sales operations.

## v0.1.0

Released scope:

- Established the initial prospecting engine foundation.
- Added Google Maps scraping capability.
- Added basic prospect data collection.
- Created the first lead-generation workflow structure.

Operational impact:

- The project moved from concept to executable lead discovery foundation.
