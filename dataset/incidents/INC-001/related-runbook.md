---
{"document_id":"checkout-db-pool-runbook-v2","document_type":"runbook","incident_id":"INC-001","service":"checkout-api","environment":"production","incident_type":"rds_connection_pool_exhaustion","severity":"SEV-2","occurred_at":"2026-07-08T10:20:00Z","valid_from":"2026-06-01","valid_until":null,"version":2,"access_scope":"checkout-team","source_path":"dataset/incidents/INC-001/related-runbook.md","section":"Diagnosis Steps"}
---
# Checkout database connection-pool exhaustion runbook

## Preconditions

Confirm that the affected service is `checkout-api` and the environment is `production`. Do not use staging pool sizes as production guidance. Begin with read-only observations.

## Diagnosis Steps

1. Compare the active ECS task definition with the most recent known-good task definition.
2. Inspect changes to `DB_MAX_POOL_SIZE`, `DB_MIN_IDLE`, and the connection acquisition timeout.
3. Check application pool active, idle, and pending counts for the incident window.
4. Compare application pool usage with the RDS `DatabaseConnections` metric.
5. Check RDS CPU as supporting context only; moderate CPU alone does not confirm database saturation.
6. If the task-definition diff or pool metrics are unavailable, report insufficient evidence rather than confirming a root cause.

## Interpretation

Connection acquisition timeouts show that callers could not obtain a pool connection. They do not, by themselves, distinguish an undersized application pool from database unavailability. The task-definition diff and database availability evidence are required to make that distinction.

## Safety

Do not restart RDS, delete the ECS service, or change production configuration as an investigative shortcut. Rollback and configuration changes require human approval and post-change verification.
