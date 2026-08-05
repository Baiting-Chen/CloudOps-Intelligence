---
{"document_id":"inventory-downstream-timeout-runbook-v2","document_type":"runbook","incident_id":"INC-002","service":"inventory-api","environment":"production","incident_type":"downstream_service_timeout","severity":"SEV-2","occurred_at":"2026-07-15T03:40:00Z","valid_from":"2026-05-10","valid_until":null,"version":2,"access_scope":"inventory-team","source_path":"dataset/incidents/INC-002/related-runbook.md","section":"Diagnosis Steps"}
---
# Inventory downstream timeout runbook

## Preconditions

Confirm that traces and metrics belong to `production`. Staging traces cannot establish the cause of a production incident. Begin with read-only observations.

## Diagnosis Steps

1. Select failed checkout trace IDs and determine whether request time is spent in checkout, inventory, or the supplier span.
2. Search inventory summaries for `SupplierTimeoutException` and compare the observed duration with the configured client deadline.
3. Check supplier timeout and error rates for the same time window.
4. Check inventory ECS CPU, memory, task count, and task-exit signals.
5. Review recent inventory deployments and configuration changes. The absence of a deployment is evidence against a recent local change, not proof against every local defect.
6. If correlated traces or dependency metrics are unavailable, report insufficient evidence and request them.

## Interpretation

HTTP 504 is a timeout symptom, not a root cause. Normal inventory CPU does not prove that a downstream provider is healthy. A supplier root-cause candidate requires correlated trace or dependency evidence.

## Safety

Do not restart checkout-api or increase the production client timeout as an investigative shortcut. Timeout changes require human approval and an assessment of retry amplification and downstream capacity.
