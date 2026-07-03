# Releases

## v0.5.0 Release Notes

`v0.5.0` is the Google Business Profile Intelligence and Elula Business Growth Assessment release.

Status: implemented locally, pending release commit and tag.

### Highlights

- Google Business Profile Intelligence foundation.
- Business Intelligence module.
- Sales Opportunity Engine.
- Internal CSV and XLSX reports.
- Branded Elula Business Growth Assessment PDF reports.
- Safe `--intelligence` CLI option.

### Business Value

This release turns available Google Maps and profile-like data into practical sales intelligence. It helps identify conservative improvement opportunities such as missing websites, low review count, missing phone details, incomplete profiles, and weak digital presence.

### Engineering Notes

- No paid Google APIs are called.
- Google Business intelligence is report-only.
- No Google Business intelligence is written to Elula BizHub.
- Existing dry-run and `--limit` behavior is preserved.

### Validation

Required:

```powershell
.venv\Scripts\python.exe -m compileall commands config integrations modules tools
.venv\Scripts\python.exe main.py execute --limit 3 --dry-run
.venv\Scripts\python.exe main.py execute --limit 3 --intelligence --dry-run
```

## v0.4.0 Release Notes

`v0.4.0` is the production-safety and intelligence-foundation release.

Status: released. Sprint 4 is complete.

### Highlights

- Persistent import history.
- Cross-run duplicate prevention.
- People enrichment framework.
- Website intelligence framework.
- Dry-run mode.
- Engineering documentation package.
- Safer validation before live Elula BizHub sync.

### Business Value

This release reduces duplicate CRM activity and prepares the system for richer sales intelligence. It allows operators to validate workflows without creating live contacts, opportunities, or tasks.

### Engineering Notes

- Import history is stored in `data/import_history.json`.
- Dry-run mode disables Elula BizHub write calls and import history writes.
- People enrichment uses an empty provider by default.
- Website intelligence performs lightweight analysis and does not write to Elula BizHub.

### Validation

Required:

```powershell
.venv\Scripts\python.exe -m compileall commands config integrations modules tools
.venv\Scripts\python.exe main.py execute --limit 3 --dry-run
```

## v0.3.0 Release Notes

`v0.3.0` formalized the Python CLI workflow and Elula BizHub operational model.

### Highlights

- CLI documentation.
- Elula BizHub terminology.
- Safe live sync with `--limit`.
- Metadata refresh command.
- Release process documentation.

### Business Value

The release made the system easier to operate and safer to test before live CRM sync.

## v0.2.0 Release Notes

`v0.2.0` improved lead processing quality.

### Highlights

- Cleaning.
- Deduplication.
- Opportunity scoring.
- Product assignment.
- Owner assignment.

### Business Value

The release improved the quality and consistency of processed prospect records.

## v0.1.0 Release Notes

`v0.1.0` established the initial prospect discovery foundation.

### Highlights

- Google Maps scraping.
- Basic prospect collection.
- Initial project structure.

### Business Value

The release proved the core prospect discovery workflow.
