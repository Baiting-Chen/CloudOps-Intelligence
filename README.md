# CloudOps Incident Intelligence

An AWS-based, evidence-grounded RAG and single-agent system for cloud incident
investigation.

## Project Goal

CloudOps Incident Intelligence is a controlled, reproducible project for
investigating cloud incidents using historical incidents, runbooks, deployment
records, alarm summaries, log summaries, and architecture documentation.

The project first builds an evaluable retrieval-augmented generation system.
After the RAG system is stable and measurable, it becomes one read-only tool
used by a bounded single-agent incident investigator.

The system must eventually:

- Retrieve historical incidents related to a current failure.
- Generate evidence-grounded Incident Briefs with traceable citations.
- Detect stale, conflicting, or insufficient evidence.
- Refuse to confirm a root cause when evidence is insufficient.
- Keep service, environment, and historical time boundaries separate.
- Require human approval for high-risk remediation actions.

## Current Status

**Phase 0: Scope and Controlled Dataset is complete.**

The repository currently contains:

- Three virtual service definitions.
- Five supported incident categories.
- Three complete Incident Packs with evaluation-only Ground Truth.
- Fifteen ingestible evidence documents.
- Twelve retrieval and generation evaluation questions.
- Four JSON Schema contracts.
- A modular dataset validator and six automated consistency tests.

The detailed completion record and current limitations are maintained in
[`docs/status.md`](docs/status.md).

The next development phase is **Phase 1: PostgreSQL Full-text Search Baseline**.

## Local Setup

Phase 0 requires Python 3.10 or later. It does not require PostgreSQL, Docker,
AWS credentials, Bedrock access, or frontend dependencies.

Create an isolated Python environment and install the development dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

The `.venv` directory is local-only and must not be committed.

## Validate the Dataset

Run the validator from the repository root:

```bash
python -m backend.app.ingestion.validate_dataset
```

The expected Phase 0 summary is:

```text
Dataset validation passed:
- 3 service definitions
- 4 schemas
- 3 Incident Packs
- 15 ingestible documents
- 12 evaluation questions
```

The command exits with status `1` and prints all detected issues when the
dataset is invalid, making it suitable for future CI use.

## Run the Test Suite

Run all tests:

```bash
python -m pytest -v
```

Run only the dataset validation tests:

```bash
python -m pytest tests/unit/test_validate_dataset.py -v
```

The tests use temporary dataset copies for failure cases. They do not modify
the repository's Incident Packs.

## Phase 0 Boundaries

Phase 0 intentionally does not include:

- PostgreSQL ingestion or retrieval.
- Vector or hybrid retrieval.
- Amazon Bedrock or other LLM calls.
- AWS resources or infrastructure as code.
- An incident investigation agent.
- Automated remediation.
- A complex frontend.
- Fabricated retrieval, generation, latency, or cost metrics.

Ground Truth is evaluation-only. It must never enter ingestion discovery,
retrieval results, embeddings, citations, or model context.

## Development Order

1. Scope and controlled dataset — complete
2. PostgreSQL full-text search baseline — next
3. Vector and hybrid retrieval
4. Evidence-grounded generation
5. RAG evaluation and quality gates
6. AWS deployment
7. Single read-only investigation agent
8. Agent evaluation
9. Reliability and human-in-the-loop remediation

## Repository Structure

```text
CloudOps-Intelligence/
├── backend/                  # Backend application and dataset validation
├── dataset/                  # Controlled source data and evaluation inputs
├── docs/                     # Scope-supporting design and status documents
├── evals/                    # Future evaluation runners and reports
├── frontend/                 # Reserved for a later user interface
├── infrastructure/           # Reserved for the AWS deployment phase
├── tests/                    # Unit, integration, evaluation, and security tests
├── PROJECT_SCOPE.md          # Long-term scope and design constraints
├── README.md                 # Setup and repository entry point
└── requirements-dev.txt      # Reproducible Phase 0 test dependency
```

See [`PROJECT_SCOPE.md`](PROJECT_SCOPE.md) for binding scope constraints,
[`docs/data-model.md`](docs/data-model.md) for data contracts, and
[`docs/implementation-plan.md`](docs/implementation-plan.md) for phase exit
criteria.
