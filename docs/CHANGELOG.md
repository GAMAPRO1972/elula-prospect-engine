# Changelog

## v0.4.0

Released scope:

- Added persistent import history.
- Added cross-run duplicate prevention.
- Added people enrichment framework.
- Added website intelligence framework.
- Added dry-run mode.
- Preserved safe `--limit` testing.
- Improved sync summary counters.
- Added permanent documentation package.

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
