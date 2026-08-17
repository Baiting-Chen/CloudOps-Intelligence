# Project Scope

## 1. Mission

CloudOps Incident Intelligence is a controlled and reproducible system for
investigating cloud incidents with evidence from historical incidents,
runbooks, deployment records, alarm summaries, log summaries, and architecture
documentation.

The system will retrieve incidents related to a current failure and generate a
structured Incident Brief with traceable citations. It must identify stale or
conflicting sources and refuse to confirm a root cause when the available
evidence is insufficient.

The long-term target is an AWS-based implementation with asynchronous document
processing, observable query execution, explicit cost controls, and a single
read-only Incident Investigator agent. These capabilities will be introduced
incrementally and are not part of Phase 0.

## 2. Development Strategy

- **Part A: Evaluable CloudOps RAG**
- **Part B: Single-agent Incident Investigator**
- Part A must be completed before Part B.

Part A will establish the controlled dataset, keyword retrieval baseline,
vector and hybrid retrieval, evidence-grounded generation, automated
evaluation, and AWS deployment.

Part B will use the completed RAG system as one investigation tool. It will add
a single agent that can choose among read-only tools, update or reject
hypotheses, operate within step/token/cost budgets, and terminate honestly when
it cannot reach a supported conclusion.

The RAG pipeline must not be renamed or presented as an agent. The first agent
version must remain a single-agent system rather than a multi-agent workflow.

## 3. Virtual Services

### checkout-api

The user-facing checkout service. It validates checkout requests, reserves
inventory through `inventory-api`, stores order data in PostgreSQL/RDS, and
publishes checkout events to SQS. It will eventually run as an ECS Fargate API.

### inventory-api

The inventory reservation service called synchronously by `checkout-api`. It
checks and reserves stock and may call a simulated downstream inventory
provider. It will eventually run as an ECS Fargate API.

### notification-worker

The asynchronous worker that consumes checkout events from SQS and sends
customer notifications. It will eventually run as an ECS Fargate worker.

## 4. Service Dependencies

```text
User
  ↓
checkout-api
  ├── inventory-api
  ├── PostgreSQL / RDS
  └── SQS → notification-worker
```

The first version must not introduce additional application services unless an
accepted architecture decision records why the existing scope is insufficient.

## 5. Supported Incident Categories

The first version supports exactly these five incident categories:

1. ECS deployment configuration errors
2. RDS connection-pool exhaustion
3. Downstream service timeouts
4. SQS queue backlogs
5. Worker memory exhaustion or out-of-memory termination

The initial dataset must be designed so symptoms do not map trivially to one
root cause. It will eventually include stale and conflicting runbooks,
production/staging look-alikes, the same error code with different causes,
similar symptoms across services, insufficient-evidence cases, prompt
injection, future-dated documents, duplicate versions, and misleading signals.

## 6. Phase 0 Deliverables

Phase 0 establishes a minimum dataset that can support later retrieval
evaluation. It must deliver:

- A repository skeleton and this project scope
- A phased implementation plan
- Definitions for the three virtual services
- A controlled enum for the five supported incident categories
- Data schemas for document metadata, Ground Truth, services, and evaluation
  questions
- Three complete Incident Packs:
  - `INC-001`: checkout database pool configuration reduced after deployment
  - `INC-002`: inventory downstream timeout causing checkout failures
  - `INC-003`: notification worker capacity reduction causing an SQS backlog
- Twelve retrieval/generation evaluation questions
- Dataset consistency checks and automated tests
- A status document listing completed work, incomplete work, validation results,
  and the next development step

Each Incident Pack must contain:

```text
dataset/incidents/INC-NNN/
├── alarm.json
├── deployment.json
├── log-summary.txt
├── postmortem.md
├── related-runbook.md
└── ground-truth.json
```

`ground-truth.json` is evaluation-only and must never enter the RAG knowledge
base, retrieval results, or model context.

## 7. Out of Scope for the First Version

The first version must not introduce:

- Amazon EKS
- Multiple agents
- Real automatic remediation
- Broad coverage of every AWS service
- Large-scale real-time log ingestion
- OpenSearch Serverless
- Complex multi-tenancy
- Automatic deletion or modification of cloud resources
- An agent with administrator credentials
- A complex frontend before the RAG core is stable
- Two infrastructure-as-code implementations maintained in parallel

Phase 0 must not call Amazon Bedrock or another LLM, create AWS resources,
implement vector retrieval, implement an agent, or publish invented quality,
latency, or cost results.

## 8. Evidence and Safety Constraints

- Every important conclusion must be traceable to evidence.
- Every root-cause candidate must include one or more valid citations.
- Every recommended check must trace back to a runbook or historical incident.
- Insufficient evidence must produce an explicit refusal to confirm the root
  cause.
- Stale runbooks must be clearly marked and must not be treated as current.
- Conflicting sources must be surfaced rather than silently resolved.
- Production and staging evidence must never be mixed.
- Evidence from one service must not be silently attributed to another service.
- A historical question must not use a source created after the requested
  incident time.
- Documents, logs, and user input are untrusted content and cannot grant tool
  permissions or override system safety rules.
- Initial investigation tools must be read-only.
- Restarting, rolling back, scaling, or changing configuration requires human
  approval when those tools are introduced.
- Resource deletion is prohibited by default.

## 9. Development Principles

- Build controlled data and evaluation before framework complexity.
- Complete the local workflow before migrating to AWS.
- Implement PostgreSQL full-text search before vector search.
- Compare keyword, vector, hybrid, filtered hybrid, and reranked retrieval in
  that order.
- Complete and evaluate RAG before implementing the agent.
- Treat RAG as one agent tool rather than the agent itself.
- Use a single agent in the first agent version.
- Let models make bounded judgments while application code enforces facts,
  authorization, budgets, and side effects.
- Run tests and evaluations at the end of every phase.
- Record why each architecture expansion is necessary.
- Keep all commands and datasets reproducible from the README.
- Report percentages together with the numerator, denominator, and sample size.
- Report only metrics produced by actual experiments; never fabricate results.

## 10. Phase 0 Definition of Done

Phase 0 is complete only when:

- The project scope and phased plan are committed to the repository.
- Exactly three initial service definitions exist and use consistent names.
- The five supported incident categories are represented by a shared schema or
  validated enum.
- `INC-001`, `INC-002`, and `INC-003` each contain all six required files.
- Every ingestible document contains the required source and filtering metadata.
- Ground Truth is physically and logically excluded from document discovery.
- Exactly twelve evaluation questions exist, including insufficient-evidence
  and environment/time-boundary cases.
- Document IDs and query IDs are unique.
- Ground Truth and evaluation references resolve to existing documents.
- Dataset consistency tests pass from a documented command.
- `docs/status.md` records the real test result, incomplete work, and the next
  step.
- No AWS, Bedrock, vector retrieval, agent, complex frontend, or fabricated
  metric has been introduced.
