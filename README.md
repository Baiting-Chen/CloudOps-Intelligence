# CloudOps Incident Intelligence

An AWS-based, evidence-grounded RAG and single-agent system for cloud incident investigation.

## Project Goal

CloudOps Incident Intelligence is a controlled, reproducible project for investigating cloud incidents using historical incidents, runbooks, deployment records, alarm summaries, and architecture documentation.

The project will first build an evaluable retrieval-augmented generation system. After the RAG system is stable and measurable, it will be exposed as one of the tools used by a single read-only incident investigation agent.

The system must:

- Retrieve historical incidents related to a current failure.
- Generate evidence-grounded incident briefs with traceable citations.
- Detect stale, conflicting, or insufficient evidence.
- Refuse to confirm a root cause when the evidence is insufficient.
- Keep service, environment, and historical time boundaries separate.
- Require human approval for high-risk remediation actions.

## Current Phase

**Phase 0: Scope and Dataset**

The current phase only establishes:

- Project scope and development constraints
- Three virtual service definitions
- Five supported incident categories
- Three initial Incident Packs
- Evaluation Ground Truth
- Twelve evaluation questions
- Data schemas
- Dataset consistency tests

## Out of Scope for Phase 0

Phase 0 does not include:

- Amazon Bedrock or other LLM calls
- AWS resource creation
- Vector or hybrid retrieval
- An incident investigation agent
- Automated remediation
- A complex frontend
- Fabricated performance or quality metrics

## Development Order

1. Scope and controlled dataset
2. PostgreSQL full-text search baseline
3. Vector and hybrid retrieval
4. Evidence-grounded generation
5. RAG evaluation
6. AWS deployment
7. Single read-only investigation agent
8. Agent evaluation
9. Reliability and human-in-the-loop remediation

## Repository Structure

```text
CloudOps-Intelligence/
├── backend/
├── frontend/
├── dataset/
├── evals/
├── docs/
├── infrastructure/
├── tests/
├── PROJECT_SCOPE.md
└── README.md
