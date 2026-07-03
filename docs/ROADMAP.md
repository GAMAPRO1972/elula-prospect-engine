# Roadmap

## Roadmap Principles

- Build production safety before automation scale.
- Keep Elula BizHub as the central operating platform.
- Prioritize qualified appointments over raw lead volume.
- Add intelligence layers incrementally.
- Clearly separate implemented, planned, and future work.

## Completed Releases

### v0.1 - Foundation

Status: implemented.

Purpose:

- establish the initial prospecting engine foundation;
- support Google Maps prospect discovery;
- create the first executable lead-generation workflow.

Outcome:

- the project moved from concept to working prospect discovery foundation.

### v0.2 - Processing

Status: implemented.

Purpose:

- convert raw lead data into cleaner prospect records;
- add cleaning, deduplication, scoring, product assignment, and owner assignment.

Outcome:

- campaign outputs became more consistent and operationally useful.

### v0.3 - Elula BizHub Integration

Status: implemented.

Purpose:

- connect processed prospects to Elula BizHub;
- add metadata refresh;
- support contact upsert, opportunity creation, task creation, and safe `--limit` testing.

Outcome:

- the system became a controlled prospect-to-CRM workflow.

### v0.4 - Production Platform

Status: implemented.

Purpose:

- add production safety and intelligence foundations;
- prevent duplicate imports across runs;
- add people enrichment framework;
- add website intelligence framework;
- add dry-run mode;
- create long-term engineering documentation.

Outcome:

- the system can be validated safely and extended toward richer sales intelligence.

### v0.5 - Google Business Profile Intelligence

Status: implemented locally, pending release commit and tag.

Objective:

- enrich prospects with Google business profile signals before sales follow-up.

Sprint 5 must begin with:

- sprint plan;
- architecture review;
- acceptance criteria;
- dry-run validation plan;
- documentation update plan.

Expected scope:

- profile completeness;
- review rating and review volume;
- category alignment;
- profile quality indicators;
- sales findings and recommendations.
- internal CSV and XLSX reports;
- Elula Business Growth Assessment PDFs.

## Planned Releases

### v0.6 - Decision Maker Discovery

Status: planned.

Objective:

- attach real decision makers to imported businesses.

Expected scope:

- provider-backed people enrichment;
- role and seniority classification;
- confidence scoring;
- source tracking;
- approved Elula BizHub mapping.

### v0.7 - AI Call Preparation

Status: planned.

Objective:

- generate practical call-prep briefs for sales owners.

Expected scope:

- business context summaries;
- likely pain points;
- recommended product positioning;
- discovery questions;
- appointment-focused call prompts.

### v0.8 - AI Outreach

Status: planned.

Objective:

- support controlled AI-assisted outreach.

Expected scope:

- WhatsApp and email draft generation;
- campaign-specific messaging rules;
- approval workflows;
- outcome tracking.

### v0.9 - Sales Intelligence Platform

Status: future.

Objective:

- turn the Prospect Engine into a measurable sales intelligence operation.

Expected scope:

- reporting dashboards;
- lead source quality metrics;
- processing and sync performance metrics;
- appointment outcome tracking;
- campaign templates and playbooks.

### v1.0 - Commercial Release

Status: future.

Objective:

- release a stable commercial-grade platform.

Expected scope:

- hardened deployment;
- production monitoring;
- release packaging;
- data retention rules;
- live sync governance;
- support process.
