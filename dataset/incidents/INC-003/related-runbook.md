---
{"document_id":"notification-sqs-backlog-runbook-v1","document_type":"runbook","incident_id":"INC-003","service":"notification-worker","environment":"production","incident_type":"sqs_queue_backlog","severity":"SEV-3","occurred_at":"2026-07-22T08:30:00Z","valid_from":"2026-06-15","valid_until":null,"version":1,"access_scope":"notifications-team","source_path":"dataset/incidents/INC-003/related-runbook.md","section":"Diagnosis Steps"}
---
# Notification SQS backlog runbook

## Preconditions

Confirm that queue metrics and worker configuration belong to `production`. Begin with read-only observations and use the same time window for rate comparisons.

## Diagnosis Steps

1. Compare message publish rate with delete or processing rate over the same window.
2. Check oldest-message age, visible-message count, and whether each trend is growing or draining.
3. Compare ECS running count and desired count with the last known-good service configuration.
4. Check per-task throughput, task exits, memory utilization, and `OutOfMemoryError` signatures.
5. Check notification-provider throttling and SQS visibility-timeout expirations.
6. Distinguish lost aggregate capacity from slow or failing individual workers before proposing remediation.
7. If deployment or configuration history is unavailable, report that the root cause cannot yet be confirmed.

## Interpretation

A backlog forms when the sustained publish rate exceeds the sustained processing rate. Queue depth alone does not distinguish reduced worker count, slow workers, provider throttling, OOM, or visibility-timeout failures. Configuration, task, and rate evidence are required.

## Safety

Never purge or delete the queue to clear a backlog. Scaling or configuration restoration requires human approval and must be followed by verification that oldest-message age is declining.
