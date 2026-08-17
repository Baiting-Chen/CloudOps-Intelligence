---
{"document_id":"INC-001-postmortem","document_type":"postmortem","incident_id":"INC-001","service":"checkout-api","environment":"production","incident_type":"rds_connection_pool_exhaustion","severity":"SEV-2","occurred_at":"2026-07-08T10:20:00Z","valid_from":"2026-07-09","valid_until":null,"version":1,"access_scope":"checkout-team","source_path":"dataset/incidents/INC-001/postmortem.md","section":"Root Cause and Evidence"}
---
# INC-001: Checkout latency after task definition 42

## Impact

From 10:20Z to 10:47Z, 7.8% of production checkout requests failed and P95 request latency reached 4.82 seconds.

## Timeline

- 10:05Z: `checkout-api:42` reached steady state.
- 10:20Z: the checkout P95 latency alarm entered the ALARM state.
- 10:31Z: responders compared task definitions 41 and 42.
- 10:39Z: configuration was restored through the approved rollback procedure.
- 10:47Z: connection wait time and checkout latency returned to baseline.

## Root Cause

Task definition 42 reduced `DB_MAX_POOL_SIZE` from 40 to 8 and `DB_MIN_IDLE` from 10 to 2. Normal production concurrency occupied all eight available application pool connections, causing new requests to wait for a connection and time out.

The deployment configuration caused application connection-pool exhaustion. The RDS instance remained available throughout the incident.

## Supporting Evidence

- The task-definition diff records the pool-size reduction.
- Application logs show the pool at 8 of 8 active connections and a peak of 73 pending acquisition requests.
- Connection waits and checkout latency began after task definition 42 was deployed.
- Both signals recovered after the approved rollback restored the previous configuration.

## Misleading Signal

RDS CPU increased from 42% to 58%. This correlated with request load but remained below the 80% saturation threshold. It is not evidence that RDS CPU saturation was the root cause.

## Safe First Checks

Compare the active and previous task definitions, inspect `DB_MAX_POOL_SIZE` and `DB_MIN_IDLE`, and compare application pool usage with the RDS database connection count.

Restarting RDS or deleting the ECS service is not a diagnostic step. Any rollback or production configuration change requires an approved remediation plan.
