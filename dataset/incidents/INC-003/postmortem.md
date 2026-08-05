---
{"document_id":"INC-003-postmortem","document_type":"postmortem","incident_id":"INC-003","service":"notification-worker","environment":"production","incident_type":"sqs_queue_backlog","severity":"SEV-3","occurred_at":"2026-07-22T08:30:00Z","valid_from":"2026-07-23","valid_until":null,"version":1,"access_scope":"notifications-team","source_path":"dataset/incidents/INC-003/postmortem.md","section":"Root Cause and Evidence"}
---
# INC-003: Notification queue backlog after worker capacity reduction

## Impact

Customer notifications were delayed by up to 31 minutes. Checkout requests and event publication remained available.

## Timeline

- 08:10Z: notification-worker task definition 29 and its service configuration were applied.
- 08:30Z: the oldest-message alarm entered the ALARM state.
- 08:36Z: responders compared publish rate, processing rate, and worker task count.
- 08:42Z: the desired-count reduction was identified in the service configuration diff.
- 08:55Z: an approved restoration returned the desired count to six.
- 09:19Z: queue age and visible-message count returned to their normal ranges.

## Root Cause

Task definition 29 preserved per-task concurrency and memory, but the associated production service configuration reduced the desired count from six workers to two. Aggregate processing capacity fell below the normal event publish rate, causing the SQS backlog.

## Supporting Evidence

- The service configuration diff records the desired-count reduction at 08:10Z.
- Per-task throughput remained near 119 messages per minute.
- Aggregate throughput fell from approximately 714 to 238 messages per minute while the publish rate remained near 705.
- Logs show successful acknowledgements and no OOM, crash loop, provider throttle, or visibility-timeout problem.
- Queue age declined after the approved restoration returned the desired count to six.

## Misleading Signals

Low aggregate worker CPU and memory were consequences of having fewer running tasks. They are not evidence that the queue was idle or that individual workers had sufficient aggregate capacity.

## Safe First Checks

Compare publish and processing rates over the same window, inspect running and desired task count, and review the latest service configuration before assigning a root cause.

Do not purge the queue or delete and recreate the ECS service. Scaling or configuration restoration requires an approved plan and verification that queue age is declining.
