"""Validation rules for the Phase 0 JSON Schema documents.

The project does not yet depend on a JSON Schema runtime. These checks protect
the schema files themselves and detect drift between schema-required fields and
the Python consistency validators.
"""

from __future__ import annotations

import json
from typing import Any

from .common import load_json
from .contracts import (
    GROUND_TRUTH_FIELDS,
    METADATA_FIELDS,
    QUESTION_FIELDS,
    SCHEMA_FILES,
    SERVICE_FIELDS,
)
from .models import ValidationContext, ValidationIssue


def _validate_local_references(
    schema: dict[str, Any],
    label: str,
    issues: list[ValidationIssue],
) -> None:
    """Ensure every local JSON Pointer reference resolves within its schema."""

    def walk(value: Any) -> None:
        """Recursively inspect dictionaries and arrays for local references."""

        if isinstance(value, dict):
            reference = value.get("$ref")
            if isinstance(reference, str) and reference.startswith("#/"):
                target: Any = schema
                try:
                    for token in reference[2:].split("/"):
                        decoded = token.replace("~1", "/").replace("~0", "~")
                        target = target[decoded]
                except (KeyError, TypeError):
                    issues.append(ValidationIssue(label, f"unresolvable local $ref: {reference}"))
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(schema)


def validate_schema_files(
    context: ValidationContext,
    issues: list[ValidationIssue],
) -> None:
    """Validate the schema inventory, dialect, strictness, and field contracts."""

    schema_root = context.dataset_root / "schemas"
    paths = sorted(schema_root.glob("*.schema.json"))
    actual = {path.name for path in paths if path.is_file()}
    if actual != SCHEMA_FILES:
        issues.append(
            ValidationIssue(
                context.relative(schema_root),
                f"expected schemas {sorted(SCHEMA_FILES)}, got {sorted(actual)}",
            )
        )

    loaded: dict[str, dict[str, Any]] = {}
    for path in paths:
        label = context.relative(path)
        try:
            schema = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(ValidationIssue(label, f"invalid JSON: {exc}"))
            continue
        if not isinstance(schema, dict):
            issues.append(ValidationIssue(label, "schema must be a JSON object"))
            continue
        loaded[path.name] = schema
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            issues.append(ValidationIssue(label, "must use JSON Schema draft 2020-12"))
        if schema.get("type") != "object":
            issues.append(ValidationIssue(label, "top-level type must be object"))
        if schema.get("additionalProperties") is not False:
            issues.append(ValidationIssue(label, "must reject additional top-level properties"))
        _validate_local_references(schema, label, issues)

    expected_required_fields = {
        "document-metadata.schema.json": METADATA_FIELDS,
        "ground-truth.schema.json": GROUND_TRUTH_FIELDS,
        "service.schema.json": SERVICE_FIELDS,
    }
    for filename, expected in expected_required_fields.items():
        schema = loaded.get(filename)
        if schema is None:
            continue
        required = schema.get("required")
        if not isinstance(required, list) or set(required) != expected:
            issues.append(
                ValidationIssue(
                    f"dataset/schemas/{filename}",
                    "required fields do not match the validator contract",
                )
            )

    eval_schema = loaded.get("eval-questions.schema.json")
    if eval_schema is None:
        return
    try:
        question_required = set(eval_schema["$defs"]["question"]["required"])
    except (KeyError, TypeError):
        issues.append(
            ValidationIssue(
                "dataset/schemas/eval-questions.schema.json",
                "missing $defs.question.required",
            )
        )
    else:
        if question_required != QUESTION_FIELDS:
            issues.append(
                ValidationIssue(
                    "dataset/schemas/eval-questions.schema.json",
                    "question fields do not match the validator contract",
                )
            )
