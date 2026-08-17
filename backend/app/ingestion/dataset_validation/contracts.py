"""Static Phase 0 dataset contracts shared by domain validators.

These constants intentionally mirror the controlled dataset specification.
Keeping them in one module prevents service, incident, and evaluation
validators from silently adopting different allowed values.
"""

from __future__ import annotations

import re


SERVICES = {"checkout-api", "inventory-api", "notification-worker"}
ENVIRONMENTS = {"production", "staging"}
INCIDENT_TYPES = {
    "ecs_deployment_misconfiguration",
    "rds_connection_pool_exhaustion",
    "downstream_service_timeout",
    "sqs_queue_backlog",
    "worker_out_of_memory",
}
DOCUMENT_TYPES = {
    "architecture",
    "runbook",
    "postmortem",
    "alarm_summary",
    "deployment",
    "log_summary",
    "distractor",
}
SEVERITIES = {"SEV-1", "SEV-2", "SEV-3", "SEV-4"}
RUNTIMES = {"ecs-fargate-api", "ecs-fargate-worker"}

METADATA_FIELDS = {
    "document_id",
    "document_type",
    "incident_id",
    "service",
    "environment",
    "incident_type",
    "severity",
    "occurred_at",
    "valid_from",
    "valid_until",
    "version",
    "access_scope",
    "source_path",
    "section",
}
PACK_FILES = {
    "alarm.json",
    "deployment.json",
    "log-summary.txt",
    "postmortem.md",
    "related-runbook.md",
    "ground-truth.json",
}
GROUND_TRUTH_FIELDS = {
    "incident_id",
    "service",
    "environment",
    "incident_type",
    "occurred_at",
    "root_cause",
    "relevant_documents",
    "required_checks",
    "optional_checks",
    "unsafe_actions",
    "misleading_signals",
}
QUESTION_FIELDS = {
    "query_id",
    "query",
    "filters",
    "as_of",
    "relevant_documents",
    "expected_facts",
    "forbidden_claims",
    "should_refuse",
}
SERVICE_FIELDS = {
    "service",
    "runtime",
    "responsibility",
    "dependencies",
    "owned_resources",
    "signals",
    "access_scope",
}
SCHEMA_FILES = {
    "document-metadata.schema.json",
    "ground-truth.schema.json",
    "eval-questions.schema.json",
    "service.schema.json",
}
EXPECTED_INCIDENTS = {"INC-001", "INC-002", "INC-003"}
EXPECTED_QUERY_IDS = {f"Q-{number:03d}" for number in range(1, 13)}

DOCUMENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
INCIDENT_ID_PATTERN = re.compile(r"^INC-[0-9]{3}$")
QUERY_ID_PATTERN = re.compile(r"^Q-[0-9]{3}$")
NORMALIZED_LABEL_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
KEBAB_CASE_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SIGNAL_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_]*$")
