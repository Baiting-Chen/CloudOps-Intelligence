# Project Status

## Status Metadata

- **Last updated:** 2026-08-17
- **Completed phase:** Phase 0 — Scope and Controlled Dataset
- **Next phase:** Phase 1 — PostgreSQL Full-text Search Baseline
- **Repository mode:** Local-only; no AWS resources or external model calls

## Phase 0 Outcome

Phase 0 is complete. The repository now provides a controlled, reproducible
minimum dataset with explicit Ground Truth, stable metadata contracts, and
automated consistency validation. This dataset is the frozen starting point for
the first keyword-retrieval baseline.

## Completed Deliverables

- Defined the long-term project scope and phased implementation order.
- Defined the `checkout-api`, `inventory-api`, and `notification-worker`
  services and their dependencies.
- Defined the five supported Phase 0 incident categories.
- Documented metadata, Incident Pack, Ground Truth, and evaluation-question
  semantics.
- Added four JSON Schema files for document metadata, Ground Truth, service
  definitions, and evaluation questions.
- Added three complete Incident Packs:
  - `INC-001`: checkout database pool configuration reduced after deployment.
  - `INC-002`: inventory downstream timeout causing checkout failures.
  - `INC-003`: notification worker capacity reduction causing an SQS backlog.
- Added twelve evaluation questions, including refusal and boundary cases.
- Implemented modular dataset validation for schema, service, document,
  Incident Pack, Ground Truth, and question consistency.
- Explicitly excluded `ground-truth.json` from ingestible document discovery.
- Added automated success and failure-path tests.
- Documented local environment setup, validation, and test commands in the
  README.

## Verified Dataset Inventory

The Phase 0 validation run on 2026-08-17 verified:

| Artifact | Verified count |
|---|---:|
| Service definitions | 3 |
| JSON Schema files | 4 |
| Incident Packs | 3 |
| Ingestible evidence documents | 15 |
| Evaluation questions | 12 |

Ground Truth files are present in each Incident Pack but are excluded from the
ingestible-document count.

## Verification Commands

From the repository root, activate the local environment and run:

```bash
source .venv/bin/activate
python -m backend.app.ingestion.validate_dataset
python -m pytest -v
```

The latest Phase 0 acceptance run completed with all six tests passing. These
are dataset consistency tests, not retrieval or generation evaluations.

## Validation Coverage

The current automated checks cover:

- Required file inventories and exact contract fields.
- Shared service, environment, incident-type, severity, and runtime enums.
- Globally unique document IDs and query IDs.
- Source-path, timestamp, version, and validity-range consistency.
- Agreement between Incident Pack metadata and Ground Truth.
- Resolution of Ground Truth filenames and evaluation document IDs.
- Service, environment, incident-type, and historical-validity boundaries for
  evaluation references.
- Ground Truth exclusion from discovery and direct ingestion metadata loading.
- Non-zero command exit behavior for invalid datasets.

## Intentionally Not Implemented

The following work belongs to later phases and remains intentionally absent:

- Document persistence, processing-state tracking, retry handling, and database
  migrations.
- PostgreSQL full-text retrieval and a query CLI.
- Retrieval metrics such as Recall@3, Recall@5, MRR, and NDCG.
- Embeddings, pgvector, hybrid retrieval, and reranking.
- Evidence-grounded Incident Brief generation.
- Amazon Bedrock and all other AWS resources.
- Frontend application behavior.
- Agent tools, investigation loops, checkpoints, and remediation actions.

No retrieval-quality, generation-quality, latency, token, or cost metrics are
reported because those experiments do not exist yet.

## Known Phase 0 Limitations

- The seed dataset contains only three incidents and twelve questions; it is
  designed for pipeline development rather than statistical conclusions.
- Incident Pack JSON payload validation currently focuses on shared metadata
  and cross-file consistency. Payload-specific ingestion models belong to
  Phase 1.
- The Python validator mirrors required schema contracts to detect drift; it
  does not yet use a third-party JSON Schema runtime.
- Tests currently run locally. CI quality gates are introduced only after
  evaluation automation is mature enough to define meaningful gates.

## Phase 1 Entry Conditions

Phase 1 may begin when this documentation branch is reviewed and merged, with
the following constraints preserved:

- Keep the Phase 0 dataset unchanged unless a versioned data change is required.
- Continue excluding Ground Truth at the ingestion boundary.
- Implement local PostgreSQL full-text search before vector search.
- Preserve exact operational identifiers during cleaning and chunking.
- Use semantic structure before applying a maximum chunk-length boundary.
- Produce the first Recall@5 result from an actual run with raw counts; do not
  place a target value into reports as though it were measured.

The first Phase 1 implementation task is to define the local PostgreSQL storage
model and migration for documents, versions, chunks, ingestion status, source
lineage, and full-text search fields. That design must be reviewed before the
ingestion worker or retrieval CLI is implemented.
