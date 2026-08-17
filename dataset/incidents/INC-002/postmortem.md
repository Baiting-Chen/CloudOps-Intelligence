---
{"document_id":"INC-002-postmortem","document_type":"postmortem","incident_id":"INC-002","service":"inventory-api","environment":"production","incident_type":"downstream_service_timeout","severity":"SEV-2","occurred_at":"2026-07-15T03:40:00Z","valid_from":"2026-07-16","valid_until":null,"version":1,"access_scope":"inventory-team","source_path":"dataset/incidents/INC-002/postmortem.md","section":"Root Cause and Evidence"}
---
# INC-002: Supplier timeouts propagated through inventory to checkout

## Impact

Between 03:40Z and 04:05Z, checkout-api returned HTTP 504 for 12.1% of production requests that required synchronous inventory reservation.

## Timeline

- 03:40Z: the inventory downstream-timeout alarm entered the ALARM state.
- 03:44Z: responders correlated failed checkout and inventory trace IDs.
- 03:51Z: supplier spans were confirmed to consume the 1500ms inventory client deadline.
- 04:05Z: supplier latency recovered and the timeout rate returned to baseline.

## Root Cause

The simulated `supplier-stock-api` experienced elevated response latency. Inventory-api's 1500ms client deadline expired before the supplier returned, and inventory propagated a dependency timeout to checkout.

Checkout-api and the inventory ECS tasks remained healthy. No inventory deployment or configuration change occurred during the preceding 24 hours.

## Supporting Evidence

- Distributed traces place nearly the full affected request duration in the supplier span.
- Inventory logs contain `SupplierTimeoutException` at the configured 1500ms client deadline.
- Supplier timeout rate reached 31.4% while inventory CPU remained at 37%.
- The deployment review found no inventory change in the previous 24 hours.
- Checkout 504 errors declined when supplier latency recovered.

## Misleading Signals

HTTP 504 identifies a timeout symptom but does not identify the failing component. Normal inventory CPU shows that local compute was not saturated; it does not prove that the supplier was healthy.

## Safe First Checks

Correlate checkout failures with inventory and supplier trace spans, measure the supplier timeout rate, confirm the active client deadline, and review recent inventory deployments before assigning a root cause.

Do not restart checkout-api or increase the production timeout without an approved change and an assessment of retry and capacity amplification risk.
