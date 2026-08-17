# Data Model

## 1. Purpose

Phase 0 uses file-based data to create a controlled and reproducible incident
dataset. The model must preserve source lineage, support future metadata
filtering, enforce service/environment/time boundaries, and keep evaluation
Ground Truth outside the RAG knowledge base.

The Phase 0 files are the source of truth for the initial dataset. Phase 1 will
map them into PostgreSQL document and chunk records without changing their
meaning.

## 2. Design Principles

- Prefer explicit fields over facts inferred from filenames or prose.
- Use stable machine-readable identifiers.
- Preserve the original repository-relative source path.
- Keep operational identifiers such as service names, HTTP status codes, task
  definitions, configuration keys, and exception names unchanged.
- Represent source validity separately from incident occurrence time.
- Treat documents, logs, alarms, and runbooks as untrusted content.
- Keep evaluation truth physically and logically separate from ingestible
  knowledge.
- Add database-specific fields only when Phase 1 requires them.

## 3. Shared Enumerations

The four JSON Schemas must use the same values defined in this section.

### Services

- `checkout-api`
- `inventory-api`
- `notification-worker`

### Environments

- `production`
- `staging`

### Incident Types

- `ecs_deployment_misconfiguration`
- `rds_connection_pool_exhaustion`
- `downstream_service_timeout`
- `sqs_queue_backlog`
- `worker_out_of_memory`

### Document Types

- `architecture`
- `runbook`
- `postmortem`
- `alarm_summary`
- `deployment`
- `log_summary`
- `distractor`

### Severities

- `SEV-1`
- `SEV-2`
- `SEV-3`
- `SEV-4`

### Initial Runtime Types

- `ecs-fargate-api`
- `ecs-fargate-worker`

These runtime values describe the future target environment. Their presence in
the dataset does not imply that AWS resources exist during Phase 0.

## 4. Identifier Conventions

| Identifier | Format | Example |
|---|---|---|
| Incident ID | `INC-NNN` | `INC-001` |
| Query ID | `Q-NNN` | `Q-001` |
| Document ID | Stable alphanumeric identifier with `.`, `_`, or `-` | `INC-001-postmortem` |
| Chunk ID | Generated in Phase 1 from document identity and ordinal | `INC-001-postmortem:0001` |

Document IDs and query IDs are globally unique within the dataset. Filenames
are not global identifiers.

## 5. Ingestible Document Metadata

Every ingestible Markdown, JSON, or TXT document must contain all fields below.
The metadata object is validated before content can be discovered or chunked.

| Field | Type | Description |
|---|---|---|
| `document_id` | string | Globally unique, stable document identifier |
| `document_type` | enum | Source category from the shared document-type enum |
| `incident_id` | string or null | Related Incident Pack; null only for documents not tied to one incident |
| `service` | enum | Primary service described by the document |
| `environment` | enum | Environment to which the evidence applies |
| `incident_type` | enum | Primary supported incident category |
| `severity` | enum | Severity associated with the incident or operational guidance |
| `occurred_at` | RFC 3339 timestamp | Time of the represented incident or event |
| `valid_from` | ISO 8601 date | First date on which the source was available and valid for answers |
| `valid_until` | ISO 8601 date or null | Last valid date; null means no predefined expiry |
| `version` | positive integer | Version of this logical document |
| `access_scope` | non-empty string | Authorization scope used by future server-side filtering |
| `source_path` | string | Repository-relative path beginning with `dataset/` |
| `section` | non-empty string | Original semantic section represented by the source |

### Time Semantics

`occurred_at` answers, "When did the represented incident or event happen?"

`valid_from` and `valid_until` answer, "When was this source available and
valid for use?" A postmortem written the day after an incident therefore has an
incident-time `occurred_at` and a later `valid_from`.

At Phase 0 date precision, a source is eligible for a query when:

```text
valid_from <= date(as_of)
and
(valid_until is null or date(as_of) <= valid_until)
```

This conservative rule prevents a future-created document from answering an
earlier historical question. If later requirements need timestamp-level source
availability, the schema must be versioned rather than silently changing the
meaning of `valid_from`.

`valid_until` must not precede `valid_from`.

### Version Semantics

Documents that represent different versions of the same logical source have
different `document_id` values and increasing `version` values. The validity
range determines which version is current at a query cutoff. Similar content is
not automatically considered a duplicate when its version or validity interval
is different.

## 6. Document File Formats

### JSON Documents

Ingestible JSON files contain a complete `metadata` object and one typed payload
object. The payload key describes the event type.

```json
{
  "metadata": {
    "document_id": "INC-001-alarm",
    "document_type": "alarm_summary",
    "incident_id": "INC-001",
    "service": "checkout-api",
    "environment": "production",
    "incident_type": "rds_connection_pool_exhaustion",
    "severity": "SEV-2",
    "occurred_at": "2026-07-08T10:20:00Z",
    "valid_from": "2026-07-08",
    "valid_until": null,
    "version": 1,
    "access_scope": "checkout-team",
    "source_path": "dataset/incidents/INC-001/alarm.json",
    "section": "Alarm Summary"
  },
  "alarm": {
    "name": "checkout-api-p95-latency-high",
    "state": "ALARM"
  }
}
```

Phase 0 uses `alarm` and `deployment` payload keys in Incident Packs. The
metadata Schema validates the common contract; later ingestion code validates
payload-specific fields.

### Markdown and TXT Documents

Markdown and TXT sources start with JSON-compatible front matter. JSON is used
inside the delimiters so Phase 0 validation can parse it with the Python
standard library while remaining compatible with YAML front-matter tooling.

```text
---
{"document_id":"INC-001-postmortem","document_type":"postmortem","incident_id":"INC-001","service":"checkout-api","environment":"production","incident_type":"rds_connection_pool_exhaustion","severity":"SEV-2","occurred_at":"2026-07-08T10:20:00Z","valid_from":"2026-07-09","valid_until":null,"version":1,"access_scope":"checkout-team","source_path":"dataset/incidents/INC-001/postmortem.md","section":"Root Cause and Evidence"}
---
# Document body
```

The body must be non-empty. Front matter is source metadata and must not be
included in searchable content after ingestion.

## 7. Incident Pack

Each incident is stored in a dedicated directory:

```text
dataset/incidents/INC-NNN/
├── alarm.json
├── deployment.json
├── log-summary.txt
├── postmortem.md
├── related-runbook.md
└── ground-truth.json
```

### File Roles

- `alarm.json` contains normalized alarm observations and symptoms.
- `deployment.json` contains a related deployment/configuration change or an
  explicit statement that no relevant change was found.
- `log-summary.txt` contains a controlled summary rather than large raw logs.
- `postmortem.md` contains impact, timeline, root cause, supporting evidence,
  misleading signals, and safe checks.
- `related-runbook.md` contains evidence-traceable diagnostic guidance and
  safety boundaries.
- `ground-truth.json` contains evaluation truth only.

All five ingestible files in a Pack must agree with Ground Truth on:

- `incident_id`
- Primary `service`
- `environment`
- Primary `incident_type`
- `occurred_at`

If an incident has a contributing category, it is described in the evidence
body. Phase 0 does not overload the primary `incident_type` field with multiple
values.

## 8. Ground Truth

Ground Truth uses the following structure:

```json
{
  "incident_id": "INC-001",
  "service": "checkout-api",
  "environment": "production",
  "incident_type": "rds_connection_pool_exhaustion",
  "occurred_at": "2026-07-08T10:20:00Z",
  "root_cause": "database_connection_pool_reduced",
  "relevant_documents": [
    "deployment.json",
    "postmortem.md",
    "related-runbook.md"
  ],
  "required_checks": [
    "compare_task_definition",
    "check_database_connection_count"
  ],
  "optional_checks": [
    "check_rds_cpu"
  ],
  "unsafe_actions": [
    "restart_rds",
    "delete_ecs_service"
  ],
  "misleading_signals": [
    "moderate_rds_cpu_increase"
  ]
}
```

### Ground Truth Field Semantics

| Field | Meaning |
|---|---|
| `root_cause` | Normalized evaluation label, not prose generated for users |
| `relevant_documents` | Pack-relative filenames that contain ground-truth evidence |
| `required_checks` | Checks an investigation must cover to receive full evidence credit |
| `optional_checks` | Useful but non-essential checks |
| `unsafe_actions` | Actions that must not be recommended or executed without policy approval |
| `misleading_signals` | True observations that do not establish the root cause |

`ground-truth.json` contains no ingestible metadata wrapper. Its filename is
explicitly excluded by document discovery. It must never be parsed as knowledge,
embedded, retrieved, cited, or included in model context.

## 9. Evaluation Question Set

The initial question set is stored at `dataset/eval/questions.json`:

```json
{
  "schema_version": 1,
  "questions": [
    {
      "query_id": "Q-001",
      "query": "checkout-api latency increased after a deployment. What should be checked first?",
      "filters": {
        "service": "checkout-api",
        "environment": "production"
      },
      "as_of": "2026-07-10T00:00:00Z",
      "relevant_documents": [
        "INC-001-deployment",
        "checkout-db-pool-runbook-v2"
      ],
      "expected_facts": [
        "compare task definitions",
        "inspect DB_MAX_POOL_SIZE"
      ],
      "forbidden_claims": [
        "RDS CPU saturation is the confirmed root cause"
      ],
      "should_refuse": false
    }
  ]
}
```

### Evaluation Field Semantics

- `filters` must include `service` and `environment`; `incident_type` is
  optional.
- `as_of` is an RFC 3339 cutoff used for historical validity checks.
- `relevant_documents` contains globally unique document IDs, not filenames.
- `expected_facts` contains normalized facts that a supported answer should
  cover.
- `forbidden_claims` contains claims that must not appear as supported facts.
- `should_refuse` is true when available evidence cannot support the requested
  conclusion.

A refusal question may identify documents that provide context. Those documents
must still be insufficient to confirm the forbidden conclusion. A historical or
environment-isolation refusal case may have an empty `relevant_documents`
array.

## 10. Service Definition

Each service definition is stored under `dataset/services/`:

```json
{
  "service": "checkout-api",
  "runtime": "ecs-fargate-api",
  "responsibility": "Accept checkout requests and coordinate order creation.",
  "dependencies": [
    "inventory-api",
    "postgresql-rds",
    "checkout-events-sqs"
  ],
  "owned_resources": [
    "checkout-api-ecs-service",
    "checkout-api-task-definition"
  ],
  "signals": [
    "http_5xx_rate",
    "http_p95_latency_ms",
    "db_connection_wait_ms"
  ],
  "access_scope": "checkout-team"
}
```

| Field | Type | Description |
|---|---|---|
| `service` | service enum | Stable service name |
| `runtime` | runtime enum | Future target runtime |
| `responsibility` | non-empty string | Business and operational responsibility |
| `dependencies` | unique string array | Services or resources called or consumed |
| `owned_resources` | unique non-empty string array | Resources the service owns |
| `signals` | unique non-empty string array | Important metrics or observable signals |
| `access_scope` | non-empty string | Scope authorized to access service evidence |

## 11. Future Phase 1 Document and Chunk Records

Phase 1 will map one source file to one logical document record and one or more
chunk records. The Phase 0 source files remain immutable evaluation fixtures.

A future document record will add ingestion-specific fields such as:

- Processing status
- Content hash
- Idempotency key
- Attempt count
- Error category and reason
- Ingested timestamp
- Expiry state

A future chunk record contains at least:

| Field | Description |
|---|---|
| `chunk_id` | Stable chunk identifier |
| `document_id` | Parent document identifier |
| `content` | Cleaned searchable content |
| `content_hash` | Hash of normalized content |
| `section` | Semantic section inherited or refined from source |
| `ordinal` | Zero- or one-based position, fixed consistently in implementation |
| `metadata` | Complete immutable metadata snapshot from the parent document |

Chunking must prefer Markdown headings, postmortem sections, runbook steps, and
JSON event types before applying a maximum-length boundary. Fixed character
count must not be the only strategy.

Embedding fields are intentionally absent from the Phase 0 source model and are
introduced only in Phase 2.

## 12. Schema Files

Phase 0 uses JSON Schema draft 2020-12:

| File | Validates |
|---|---|
| `dataset/schemas/document-metadata.schema.json` | Common ingestible document metadata |
| `dataset/schemas/ground-truth.schema.json` | One Incident Pack Ground Truth file |
| `dataset/schemas/eval-questions.schema.json` | The complete evaluation question set |
| `dataset/schemas/service.schema.json` | One virtual service definition |

Schemas use `additionalProperties: false` in Phase 0 so accidental fields are
detected rather than silently ignored. Schema changes require a versioned,
documented update to the data model and consistency tests.

## 13. Cross-file Consistency Invariants

Schema validation checks individual files. The dataset consistency checker must
also enforce relationships that JSON Schema alone cannot reliably express:

- The repository contains exactly the three Phase 0 Incident Packs.
- Each Pack contains exactly the six required files.
- `document_id` values are globally unique.
- `query_id` values are globally unique and initially cover `Q-001` to `Q-012`.
- Each `source_path` resolves to the document that declares it.
- Pack metadata agrees with its directory and Ground Truth.
- Every Ground Truth filename reference resolves inside its own Pack.
- Every evaluation document ID resolves to an ingestible document.
- Evaluation evidence is valid at the question's `as_of` cutoff.
- A document whose environment differs from the query filter cannot satisfy a
  relevant-document expectation.
- `ground-truth.json` is never returned by ingestible-document discovery.
- The three service definitions use the shared service enum exactly once each.
- No document, query, or Ground Truth field contains an unsupported service,
  environment, incident type, document type, severity, or runtime value.

These invariants become automated tests before Phase 0 is marked complete.
