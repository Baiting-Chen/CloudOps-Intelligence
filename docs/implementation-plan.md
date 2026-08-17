# Implementation Plan

## 1. Purpose

This document defines the required delivery order for CloudOps Incident
Intelligence. The project must advance through small, measurable phases rather
than implementing the complete RAG and agent system at once.

Each phase must produce:

- A reproducible implementation
- Automated tests appropriate to the phase
- Evaluation results produced by real executions
- Updated documentation and project status
- A clear explanation for any architecture expansion

A phase is complete only when its exit criteria are met. Work from a later
phase must not be introduced merely to demonstrate more technologies.

## 2. Required Delivery Order

```text
Phase 0: Scope and Dataset
    ↓
Phase 1: PostgreSQL Full-text Search Baseline
    ↓
Phase 2: Vector and Hybrid Retrieval
    ↓
Phase 3: Evidence-grounded Generation
    ↓
Phase 4: RAG Evaluation and Quality Gates
    ↓
Phase 5: AWS Deployment
    ↓
Phase 6: Single Read-only Investigator Agent
    ↓
Phase 7: Agent Evaluation
    ↓
Phase 8: Reliability and Human-in-the-loop Remediation
```

The RAG system must be completed and evaluated before it becomes an agent
tool. AWS deployment must not begin until the local RAG workflow has real
evaluation results.

## 3. Phase 0: Scope and Controlled Dataset

### Objective

Create a small, internally consistent, reproducible incident dataset with
explicit Ground Truth. This phase establishes the facts and evaluation inputs
that later retrieval and generation systems will be measured against.

### Deliverables

- `PROJECT_SCOPE.md`
- This phased implementation plan
- Definitions for:
  - `checkout-api`
  - `inventory-api`
  - `notification-worker`
- A controlled enum for the five supported incident categories
- Data schemas for service definitions, document metadata, Ground Truth, and
  evaluation questions
- Three Incident Packs:
  - `INC-001`: checkout database pool configuration reduced after deployment
  - `INC-002`: inventory downstream timeout causing checkout failures
  - `INC-003`: notification worker capacity reduction causing an SQS backlog
- Twelve retrieval/generation evaluation questions
- Dataset consistency validation
- Automated consistency tests
- `docs/status.md`

### Required Dataset Properties

- Every ingestible document has a globally unique `document_id`.
- Every document preserves its source, section, service, environment, incident
  type, severity, occurrence time, validity interval, version, and access scope.
- Every Incident Pack contains alarm, deployment, log summary, postmortem,
  related runbook, and evaluation-only Ground Truth files.
- Ground Truth is excluded from all future knowledge discovery and ingestion.
- Evaluation questions include expected facts, relevant document IDs,
  forbidden claims, and refusal expectations.
- The seed set includes misleading or insufficient evidence rather than only
  straightforward positive examples.

### Exit Criteria

- All three Incident Packs contain the six required files.
- Exactly twelve initial evaluation questions exist.
- Document IDs and query IDs are unique.
- All Ground Truth and evaluation references resolve.
- Source paths, services, environments, and timestamps are consistent.
- Ground Truth exclusion is covered by an automated test.
- All dataset consistency tests pass from a documented command.
- No LLM, AWS, vector retrieval, agent, or fabricated metric has been added.

## 4. Phase 1: PostgreSQL Full-text Search Baseline

### Objective

Build the first local, measurable RAG retrieval baseline using PostgreSQL
full-text search. Keyword retrieval comes before embeddings because operational
identifiers and exact values are important evidence.

### Deliverables

- Markdown, JSON, and TXT document parsing
- Metadata validation before ingestion
- Content cleaning that preserves operational identifiers
- Semantic section-aware chunking using:
  - Markdown headings
  - Postmortem sections
  - Runbook steps
  - JSON event structure
  - A maximum chunk-length boundary
- Content hashing and duplicate detection
- Idempotent ingestion
- Document version and expiry handling
- Processing status, error reason, finite retry state, and source lineage
- PostgreSQL schema and migrations
- PostgreSQL full-text index and keyword retrieval
- CLI query interface
- First real Recall@5 report

The retrieval result must include:

- `document_id`
- `chunk_id`
- Retrieval score
- Section
- Source path
- Metadata
- Matched text

### Exit Criteria

- Re-ingesting the same content does not create duplicate active chunks.
- Ground Truth cannot enter the ingestion pipeline.
- Structured chunking is tested and fixed-size splitting is not the only
  strategy.
- Exact identifiers such as `checkout-api`, `HTTP 504`, task-definition
  versions, configuration keys, and exception names are retrievable.
- The CLI returns the required result fields.
- Recall@5 is calculated from actual runs and includes raw results and sample
  counts.

## 5. Phase 2: Vector and Hybrid Retrieval

### Objective

Add semantic retrieval only after the keyword baseline is stable, then compare
retrieval methods on the same dataset and questions.

### Deliverables

- pgvector storage and migrations
- Embedding generation abstraction
- Vector-only search
- Keyword-only search retained as the baseline
- Keyword and vector fusion using Reciprocal Rank Fusion initially
- Metadata filtering for:
  - Service
  - Environment
  - Document type
  - Incident type
  - Severity
  - Occurrence time
  - Valid-from and valid-until dates
- Optional reranker added only after filtered hybrid retrieval is measured
- Retrieval comparison report covering:
  - Keyword only
  - Vector only
  - Hybrid
  - Hybrid with metadata filtering
  - Hybrid with metadata filtering and reranking

### Exit Criteria

- All retrieval strategies run against the same frozen evaluation set.
- Cross-environment errors, stale-document use, and irrelevant-document rate
  are reported separately.
- Retrieval configuration is reproducible.
- The report includes Recall@3, Recall@5, MRR, NDCG, and sample counts.
- No generation quality is claimed from retrieval metrics alone.

## 6. Phase 3: Evidence-grounded Generation

### Objective

Generate a structured Incident Brief that distinguishes supported conclusions
from hypotheses and refuses unsupported certainty.

### Required Output

```json
{
  "summary": "...",
  "similar_incidents": [],
  "root_cause_candidates": [],
  "recommended_checks": [],
  "conflicts": [],
  "stale_sources": [],
  "missing_information": [],
  "citations": [],
  "evidence_sufficient": false
}
```

### Deliverables

- Structured response schema and validation
- Citation requirements for every root-cause candidate
- Traceability requirements for every recommended check
- Explicit insufficient-evidence refusal
- Stale-source identification
- Conflicting-source detection
- Service and environment isolation
- Historical time-boundary enforcement
- Prompt-injection tests for documents and logs
- Protection against unsafe remediation recommendations

### Exit Criteria

- Unsupported root-cause confirmation is rejected.
- Every root-cause candidate and recommended check has valid source lineage.
- Stale and conflicting sources are visible in the response.
- Future-created documents cannot answer earlier historical questions.
- Production and staging evidence cannot be silently combined.
- Unsupported critical claims equal zero on the evaluated sample.

## 7. Phase 4: RAG Evaluation and Quality Gates

### Objective

Expand the dataset and automate retrieval, generation, system, cost, and
failure evaluation before deploying to AWS.

### Deliverables

- 40 to 50 evaluation questions
- 30 to 50 historical incidents over time
- Automated retrieval evaluation
- Automated generation evaluation
- Latency, token, and estimated cost reporting
- Failure classification
- CI quality gates
- Versioned raw results and summary reports

### Metrics

Retrieval metrics include Recall@3, Recall@5, MRR, NDCG, irrelevant-document
rate, stale-document misuse rate, and cross-environment false-positive rate.

Generation metrics include citation correctness, citation coverage, expected
fact coverage, unsupported-claim rate, forbidden-claim rate, correct refusal
rate, and conflict-detection accuracy.

System metrics include P50/P95 latency, tokens per query, estimated query cost,
embedding cost, ingestion failure rate, and cache hit rate.

### Internal Graduation Targets

These are project targets rather than industry standards:

- Recall@5 at least 80%
- Citation correctness at least 95%
- Unsupported critical claims equal to zero
- Correct refusal on insufficient-evidence cases at least 80%

Every percentage must include the numerator, denominator, and sample size.

### Exit Criteria

- Evaluation commands are reproducible from the README.
- Raw runs are retained rather than only the best summary.
- Quality-gate failures block promotion or are explicitly accepted with a
  documented reason.
- No invented latency, quality, token, or cost data appears in the repository.

## 8. Phase 5: AWS Deployment

### Objective

Move the evaluated local RAG workflow to AWS with clear responsibilities,
minimum permissions, observability, and cost controls.

### Preconditions

Before creating resources:

- Select Terraform or AWS CDK and maintain only one.
- Configure an AWS Budget and cost alerts.
- Define mandatory resource tags.
- Set log retention periods.
- Define how to stop and destroy the development environment.
- Limit Bedrock request and daily budgets.

### Deliverables

- S3 source-document storage with object versioning
- SQS ingestion queue and dead-letter queue
- ECS Fargate API and ingestion worker
- RDS PostgreSQL with full-text and pgvector retrieval
- Bedrock embedding and generation integrations
- CloudWatch logs, metrics, alarms, and request correlation
- IAM least-privilege roles and KMS protection
- Finite retries, failure status, DLQ handling, and manual replay
- Deployment, operations, and destruction documentation

### Exit Criteria

- Upload-to-query flow works end to end.
- Duplicate S3 events do not duplicate active content.
- Failures are bounded, observable, and replayable.
- Logs record request ID, phase latency, token use, estimated cost, retrieved
  document IDs, refusal reason, and error category.
- The environment can be stopped and destroyed using documented commands.
- Cost alarms and limits are verified before model load testing.

## 9. Phase 6: Single Read-only Investigator Agent

### Objective

Use the stable RAG system as one tool in a bounded single-agent investigation
loop. The agent must select its next action from current evidence rather than
following a hard-coded tool order.

### Read-only Tools

- `search_incident_memory`
- `retrieve_runbook`
- `get_service_metrics`
- `search_log_summary`
- `get_recent_deployments`
- `get_service_status`
- `compare_configuration_versions`

The initial tools may read controlled JSON fixtures before being replaced with
real AWS read-only APIs.

### Deliverables

- Structured investigation state
- Current and rejected hypotheses
- Evidence and missing-information tracking
- Tool-call history
- Step, token, cost, and execution-time budgets
- Repetition and no-new-evidence detection
- Structured investigation report
- Honest terminal reasons for success, insufficient evidence, permission
  failure, budget exhaustion, timeout, loop, or unsafe tool failure

### Exit Criteria

- The agent chooses tools based on observations rather than a fixed sequence.
- It can revise a hypothesis in response to contradictory evidence.
- Invalid or repeated calls are bounded.
- It does not force a root cause when evidence is insufficient.
- All available tools remain read-only.

## 10. Phase 7: Agent Evaluation

### Objective

Measure final results, complete trajectories, and individual tool decisions,
including stability across repeated executions.

### Deliverables

- 30 to 50 agent investigation tasks
- Final-result evaluation
- Trajectory evaluation
- Single-step tool-call evaluation
- Failure taxonomy
- Each task executed three to five times
- Aggregate reports containing averages and variation ranges

### Metrics

- Task success rate
- Root-cause accuracy
- Evidence coverage
- Average tool calls
- Invalid tool-call rate
- Tool failure recovery rate
- Loop rate
- Honest failure rate
- Human intervention rate
- Cost per successful investigation
- P50/P95 execution time
- Over-budget termination rate

### Exit Criteria

- Evaluation accepts multiple reasonable tool paths rather than requiring one
  exact sequence.
- Required evidence and unsafe actions are checked independently of final text.
- Repeated runs report variability rather than selecting only the best run.
- Premature completion, looping, and failure-recovery behavior are classified.

## 11. Phase 8: Reliability and Human-in-the-loop Remediation

### Objective

Add crash recovery and fault tolerance first, then introduce narrowly scoped
side-effect tools behind explicit human approval.

### Reliability Deliverables

- Checkpoint after every completed tool call
- Resume from the next incomplete step after service restart
- Model timeout and Bedrock throttling tests
- Tool timeout, partial data, permission failure, and truncated log tests
- Repeated-query and no-new-evidence loop protection
- Crash and checkpoint-recovery tests
- Cross-service, cross-environment, and prompt-injection security tests

### Human Approval Deliverables

- Evidence-backed remediation plan
- Risk and change-scope display
- Persisted suspended state while waiting for approval
- Approve, modify, and reject flows
- Execution verification
- Immutable audit record

Potential side-effect tools include service restart, task-definition rollback,
worker scaling, configuration changes, incident-ticket creation, and
notifications. Restart, rollback, scaling, and configuration changes always
require approval. Resource deletion remains prohibited.

### Exit Criteria

- Recovery does not repeat completed side effects.
- Approval waiting consumes no active investigation compute.
- Prompt or document content cannot bypass permissions or approval.
- Every approved or rejected action has a traceable audit record.
- Failure-injection tests cover the documented reliability scenarios.

## 12. Cross-phase Working Rules

At the end of every phase:

1. Run unit, integration, evaluation, and security tests that apply.
2. Save the actual command and result.
3. Update `docs/status.md` with completed and incomplete work.
4. Update the README with reproducible setup and execution instructions.
5. Record new architecture decisions and why they became necessary.
6. Commit generated reports only when their inputs and reproduction command are
   known.
7. Do not start the next phase until the current exit criteria are satisfied or
   an explicit exception is documented.
