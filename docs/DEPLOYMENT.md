# Deployment

## Current Deployment Model

The current project runs as a local Python CLI application.

Primary runtime:

- Windows PowerShell.
- Python virtual environment.
- Local `.env`.
- Local campaign files.
- Local CSV input and output folders.

## Git

Use Git for source control.

Rules:

- Run `git status` before release work.
- Do not commit unless explicitly instructed.
- Do not tag unless explicitly instructed.
- Do not push unless explicitly instructed.
- Do not include `.env`, secrets, logs, raw input files, or generated output files in commits.

## GitHub

GitHub is the expected remote repository platform.

Release pushes should happen only after:

- compile validation;
- dry-run validation;
- approved limited live validation when required;
- documentation review;
- explicit instruction to push.

## Version Tags

Use semantic version tags such as:

```text
v0.4.0
v0.5.0
v1.0.0
```

Create tags only when explicitly instructed.

## Release Process

Approved release sequence:

1. Run `git status`.
2. Confirm release scope.
3. Run compile check.
4. Run dry-run validation.
5. Run limited live validation only if approved.
6. Update documentation.
7. Commit approved files.
8. Create release tag.
9. Push branch.
10. Push tag.
11. Create ZIP backup of release state.

## ZIP Backup

A ZIP backup should capture the approved release state after validation.

Do not include:

- `.env`;
- virtual environment folders;
- logs;
- raw CSV input;
- generated output;
- secrets.

## Future VPS Deployment

Future VPS deployment should add:

- environment variable management;
- scheduled campaign execution;
- log rotation;
- monitoring;
- secure credential storage;
- backup strategy;
- operator runbooks.

VPS deployment should not happen until dry-run, duplicate prevention, and reporting are mature enough for unattended operation.

## Future Docker Deployment

Future Docker deployment should add:

- repeatable runtime environment;
- isolated dependencies;
- controlled scraper runtime;
- volume mappings for input, output, logs, and data;
- environment variable injection;
- health checks.

Docker should support safer production operations, not hide operational complexity.
