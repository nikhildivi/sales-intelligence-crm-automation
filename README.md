# Sales Intelligence & CRM Hygiene Lab
**Independent educational project — fictional accounts only.**

Normalizes company domains, identifies duplicate records, respects opt-out/suppression flags, ranks fictional lead accounts with an explainable score, and exports a CSV suitable for manual review. FastAPI `POST /v1/accounts/score`. This is NOT a working CRM integration, commercial enrichment provider, production lead-scoring model, or real outreach automation.

## Quick start
```bash
python -m pip install fastapi uvicorn pytest httpx
python sales_intelligence.py
pytest -q
uvicorn sales_intelligence:app --port 8101
```
Open `/docs` for the interactive API. Data must remain synthetic; upload no actual client records.

## Architecture
Lead schema → website normalization → duplicate detection → suppression → explainable rule-based score → analyst review → CSV export.  Rules are synthetic hypotheses, not learned or validated conversion predictors.

## Business metrics to measure in a real pilot
Duplicate rate, accepted research briefs, time-to-brief, enrichment coverage, analyst feedback, and false-positive prospect prioritization. Real CRM writes require approved credentials, scoping and audit controls.

## Added Checkwriters fit demonstrations
Expanded with RevOps opportunity-funnel reporting, QA queues, and synthetic weighted pipeline calculations. This is not a live CRM integration or actual revenue measurement.
