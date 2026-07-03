# Testing

## Testing Principles

- Validate safety before volume.
- Use dry-run before live sync.
- Use `--limit` before any larger live run.
- Never run full live sync unless explicitly instructed.
- Treat Elula BizHub writes as production actions.

## Compile Check

Run before completing code work:

```powershell
.venv\Scripts\python.exe -m compileall commands config integrations modules tools
```

Expected result:

- all listed folders compile successfully;
- no syntax errors;
- no import errors from changed modules.

## Dry Run

Dry-run is the default safe workflow validation.

```powershell
.venv\Scripts\python.exe main.py execute --limit 3 --dry-run
```

Expected behavior:

- scraper may run;
- processing may run;
- people enrichment may run;
- website intelligence may run;
- import history is not written;
- Elula BizHub contact upsert is not called;
- opportunity creation is not called;
- task creation is not called;
- summary shows what would happen.

## Limited Live Run

Only run after dry-run succeeds and live testing is approved.

```powershell
.venv\Scripts\python.exe main.py execute --limit 3
```

Expected validation:

- correct pipeline;
- correct stage;
- correct owner;
- correct tags;
- no duplicate contacts;
- no duplicate opportunities;
- no duplicate tasks;
- import history records only successful complete imports.

## Production Run

Production run means a larger or unrestricted live sync.

Rules:

- Never run it unless explicitly instructed.
- Confirm campaign configuration.
- Confirm metadata freshness.
- Confirm import history state.
- Confirm source CSV quality.
- Confirm owner availability.
- Confirm rollback or cleanup plan.

## Release Validation

Before every release:

1. Run compile check.
2. Run dry-run.
3. Review logs.
4. Review `git status`.
5. Confirm no secrets are present.
6. Confirm documentation is updated.
7. Run limited live validation only when approved.
