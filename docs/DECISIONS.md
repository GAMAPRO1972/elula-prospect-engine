# Engineering Decisions

## Python as the Core Runtime

Decision:

Use Python for the Prospect Engine.

Context:

The system needs CLI workflows, CSV processing, data cleaning, API integration, enrichment pipelines, and future AI-assisted processing.

Reason:

Python supports these workflows with low implementation overhead and strong maintainability for automation-heavy systems.

Consequences:

The project can move quickly while staying readable. Dependency control remains important because the system is intended for operational use.

Version:

`v0.1`

## Elula BizHub First

Decision:

Make Elula BizHub the first live operational integration.

Context:

Elula BizHub is the central CRM, automation, communication, task, and pipeline platform for the business.

Reason:

Prospecting output is only commercially useful when it enters the actual sales workflow.

Consequences:

The system prioritizes CRM-ready records, owner assignment, pipeline placement, and appointment follow-up over isolated lead exports.

Version:

`v0.3`

## Persistent Import History

Decision:

Use a persistent local import history ledger.

Context:

Contact upsert does not prevent duplicate opportunities or tasks across repeated prospecting runs.

Reason:

The system needs cross-run duplicate prevention before live CRM writes.

Consequences:

Prospects are skipped when already imported. The ledger must be treated as operational data and protected during dry-run validation.

Version:

`v0.4`

## Dry-Run Mode

Decision:

Add `--dry-run` to the full execution workflow.

Context:

The full workflow can create or update Elula BizHub contacts, opportunities, and tasks.

Reason:

Operators need to validate processing, enrichment, duplicate checks, and sync intent without writing live CRM data.

Consequences:

Dry-run became the required validation step before live sync. It blocks Elula BizHub writes and import history writes.

Version:

`v0.4`

## Website Intelligence Before AI

Decision:

Build website intelligence before AI call preparation.

Context:

AI outputs need reliable source signals to avoid generic or unsupported recommendations.

Reason:

Website intelligence provides structured evidence about reachability, enquiry capture, tracking, social presence, and digital maturity.

Consequences:

Future AI call preparation can reference concrete source data. Website intelligence is not written to Elula BizHub until mapping is approved.

Version:

`v0.4`

## Provider Architecture

Decision:

Use provider interfaces for enrichment systems.

Context:

People enrichment and future intelligence layers may use manual data, internal logic, or paid external APIs.

Reason:

Provider interfaces allow new data sources to be added without rewriting the processing or sync core.

Consequences:

The system can start safely with empty or manual providers and later add approved external providers.

Version:

`v0.4`

## Duplicate Prevention as a Sync Boundary Concern

Decision:

Perform persistent duplicate prevention immediately before Elula BizHub sync.

Context:

Duplicates become operationally harmful when they create repeated CRM records, opportunities, or tasks.

Reason:

Keeping duplicate prevention near the sync boundary protects live systems even if upstream data changes.

Consequences:

Processing can still export full results, while sync remains protected from repeated writes.

Version:

`v0.4`

## Documentation First for v0.4

Decision:

Create a permanent engineering documentation package after completing `v0.4.0`.

Context:

The project is becoming a long-term commercial asset with multiple future contributors and AI assistants.

Reason:

Clear documentation reduces onboarding time, preserves architectural intent, and prevents unsafe operational shortcuts.

Consequences:

`PROJECT_CONTEXT.md` becomes the authoritative onboarding document. Other docs support architecture, roadmap, testing, deployment, and decisions.

Version:

`v0.4`

## Keep Intelligence Separate From CRM Writes

Decision:

Do not write people or website intelligence into Elula BizHub yet.

Context:

The enrichment frameworks exist, but field mapping and operational usage rules are not finalized.

Reason:

Premature CRM writes can create clutter, reporting noise, and support burden.

Consequences:

People and website intelligence run safely as foundations. CRM write behavior remains stable until approved mapping is defined.

Version:

`v0.4`
