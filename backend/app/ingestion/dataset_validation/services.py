"""Consistency validation for the three Phase 0 service definitions.

Service definitions provide the shared vocabulary used by Incident Packs and
evaluation filters, so invalid identifiers are rejected before ingestion.
"""

from __future__ import annotations

import json

from .common import is_enum_value, load_json, require_exact_fields, validate_unique_string_array
from .contracts import (
    KEBAB_CASE_PATTERN,
    RUNTIMES,
    SERVICES,
    SERVICE_FIELDS,
    SIGNAL_PATTERN,
)
from .models import ValidationContext, ValidationIssue


def validate_service_definitions(
    context: ValidationContext,
    issues: list[ValidationIssue],
) -> None:
    """Validate service inventory, identifiers, ownership, and signals."""

    service_root = context.dataset_root / "services"
    expected_files = {f"{service}.json" for service in SERVICES}
    paths = sorted(service_root.glob("*.json"))
    actual_files = {path.name for path in paths}
    if actual_files != expected_files:
        issues.append(
            ValidationIssue(
                context.relative(service_root),
                f"expected service files {sorted(expected_files)}, got {sorted(actual_files)}",
            )
        )

    observed_services: set[str] = set()
    for path in paths:
        label = context.relative(path)
        try:
            payload = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(ValidationIssue(label, f"invalid JSON: {exc}"))
            continue
        if not require_exact_fields(payload, SERVICE_FIELDS, label, issues):
            continue

        service = payload["service"]
        if not is_enum_value(service, SERVICES):
            issues.append(ValidationIssue(label, f"unknown service: {service!r}"))
        elif service in observed_services:
            issues.append(ValidationIssue(label, f"duplicate service definition: {service}"))
        else:
            observed_services.add(service)
        if path.stem != service:
            issues.append(ValidationIssue(label, "filename must match the service field"))
        if not is_enum_value(payload["runtime"], RUNTIMES):
            issues.append(ValidationIssue(label, f"unknown runtime: {payload['runtime']!r}"))
        if not isinstance(payload["responsibility"], str) or not payload[
            "responsibility"
        ].strip():
            issues.append(ValidationIssue(label, "responsibility must be a non-empty string"))
        validate_unique_string_array(
            payload["dependencies"],
            "dependencies",
            label,
            issues,
            allow_empty=False,
            pattern=KEBAB_CASE_PATTERN,
        )
        validate_unique_string_array(
            payload["owned_resources"],
            "owned_resources",
            label,
            issues,
            allow_empty=False,
            pattern=KEBAB_CASE_PATTERN,
        )
        validate_unique_string_array(
            payload["signals"],
            "signals",
            label,
            issues,
            allow_empty=False,
            pattern=SIGNAL_PATTERN,
        )
        access_scope = payload["access_scope"]
        if not isinstance(access_scope, str) or KEBAB_CASE_PATTERN.fullmatch(access_scope) is None:
            issues.append(ValidationIssue(label, "access_scope must be a kebab-case identifier"))
