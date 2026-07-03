# Engineering Decisions

## Why Python

Python is appropriate for this project because it is effective for CLI workflows, CSV processing, data cleaning, API integrations, enrichment pipelines, and future AI-assisted processing.

It keeps implementation speed high while remaining maintainable for operational automation.

## Why Elula BizHub First

Elula BizHub is the central CRM and operations platform for contacts, opportunities, communications, tasks, and pipeline management.

Syncing into Elula BizHub first ensures the Prospect Engine supports the actual sales workflow instead of producing disconnected lead files.

## Why Import History

Elula BizHub upsert behavior alone does not prevent duplicate opportunities or tasks across repeated runs.

Persistent import history provides cross-run duplicate prevention by recording successful full imports and skipping previously imported prospects before CRM writes occur.

## Why Dry Run

Dry-run mode allows the full workflow to be validated without creating or updating live Elula BizHub records.

This is mandatory for production safety because prospecting workflows can create CRM data at scale.

## Why Website Intelligence Before AI

AI call preparation needs reliable source signals.

Website intelligence provides structured, explainable data about reachability, enquiry capture, tracking, social presence, and digital maturity before adding AI interpretation.

## Why Provider Architecture

People enrichment and future external intelligence sources may require paid APIs or multiple providers.

Provider interfaces allow new data sources to be added without rewriting the core processing or sync logic.

## Why Duplicate Prevention

Duplicate contacts, opportunities, and tasks create operational noise and reduce trust in the CRM.

Duplicate prevention protects sales owners, reporting accuracy, and campaign scalability.

## Why Documentation First

The system is becoming a long-term commercial asset.

Permanent documentation reduces onboarding time, improves handoffs between human and AI engineers, and keeps release decisions aligned with business objectives.

## Why Keep Intelligence Separate From CRM Writes

People and website intelligence are currently frameworks.

Keeping them separate from Elula BizHub writes avoids premature field mapping, prevents CRM clutter, and allows the intelligence model to mature before operational rollout.
