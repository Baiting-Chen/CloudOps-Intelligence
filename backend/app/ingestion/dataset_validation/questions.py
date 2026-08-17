"""Validation rules for retrieval and generation evaluation questions.

Question validation resolves document references and enforces service,
environment, incident-type, and historical-validity constraints against the
Incident Pack evidence index.
"""

from __future__ import annotations

import json

from .common import (
    is_enum_value,
    load_json,
    parse_date,
    parse_datetime,
    require_exact_fields,
    validate_unique_string_array,
)
from .contracts import (
    ENVIRONMENTS,
    EXPECTED_QUERY_IDS,
    INCIDENT_TYPES,
    QUERY_ID_PATTERN,
    QUESTION_FIELDS,
    SERVICES,
)
from .models import DocumentRecord, ValidationContext, ValidationIssue


def validate_questions(
    documents: dict[str, DocumentRecord],
    context: ValidationContext,
    issues: list[ValidationIssue],
) -> None:
    """Validate question structure, references, filters, and temporal safety."""

    path = context.dataset_root / "eval" / "questions.json"
    label = context.relative(path)
    try:
        payload = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(ValidationIssue(label, f"invalid JSON: {exc}"))
        return

    if not isinstance(payload, dict) or set(payload) != {"schema_version", "questions"}:
        issues.append(
            ValidationIssue(label, "top-level fields must be schema_version and questions")
        )
        return
    if payload["schema_version"] != 1:
        issues.append(ValidationIssue(label, "schema_version must equal 1"))
    questions = payload["questions"]
    if not isinstance(questions, list):
        issues.append(ValidationIssue(label, "questions must be an array"))
        return
    if len(questions) != 12:
        issues.append(ValidationIssue(label, "Phase 0 requires exactly 12 questions"))

    query_ids: set[str] = set()
    allowed_filter_fields = {"service", "environment", "incident_type"}
    for index, question in enumerate(questions):
        question_label = f"{label}#questions[{index}]"
        if not require_exact_fields(question, QUESTION_FIELDS, question_label, issues):
            continue

        query_id = question["query_id"]
        if not isinstance(query_id, str) or QUERY_ID_PATTERN.fullmatch(query_id) is None:
            issues.append(ValidationIssue(question_label, "query_id has an invalid format"))
        elif query_id in query_ids:
            issues.append(ValidationIssue(question_label, f"duplicate query_id: {query_id}"))
        else:
            query_ids.add(query_id)
        if not isinstance(question["query"], str) or not question["query"].strip():
            issues.append(ValidationIssue(question_label, "query must be a non-empty string"))

        filters = question["filters"]
        filters_valid = isinstance(filters, dict)
        if not filters_valid:
            issues.append(ValidationIssue(question_label, "filters must be an object"))
        else:
            unexpected = sorted(set(filters) - allowed_filter_fields)
            missing = sorted({"service", "environment"} - set(filters))
            if unexpected:
                issues.append(
                    ValidationIssue(
                        question_label,
                        f"unexpected filter fields: {', '.join(unexpected)}",
                    )
                )
            if missing:
                issues.append(
                    ValidationIssue(
                        question_label,
                        f"missing filter fields: {', '.join(missing)}",
                    )
                )
            if not is_enum_value(filters.get("service"), SERVICES):
                issues.append(ValidationIssue(question_label, "filter service is invalid"))
            if not is_enum_value(filters.get("environment"), ENVIRONMENTS):
                issues.append(ValidationIssue(question_label, "filter environment is invalid"))
            if "incident_type" in filters and not is_enum_value(
                filters["incident_type"], INCIDENT_TYPES
            ):
                issues.append(ValidationIssue(question_label, "filter incident_type is invalid"))

        try:
            as_of = parse_datetime(question["as_of"])
        except (TypeError, ValueError) as exc:
            issues.append(ValidationIssue(question_label, f"invalid as_of: {exc}"))
            as_of = None

        relevant_valid = validate_unique_string_array(
            question["relevant_documents"],
            "relevant_documents",
            question_label,
            issues,
        )
        validate_unique_string_array(
            question["expected_facts"],
            "expected_facts",
            question_label,
            issues,
            allow_empty=False,
        )
        validate_unique_string_array(
            question["forbidden_claims"],
            "forbidden_claims",
            question_label,
            issues,
            allow_empty=False,
        )
        if not isinstance(question["should_refuse"], bool):
            issues.append(ValidationIssue(question_label, "should_refuse must be boolean"))

        if not relevant_valid:
            continue
        for document_id in question["relevant_documents"]:
            record = documents.get(document_id)
            if record is None:
                issues.append(
                    ValidationIssue(
                        question_label,
                        f"unknown relevant document_id: {document_id}",
                    )
                )
                continue
            metadata = record.metadata
            if filters_valid:
                if metadata.get("service") != filters.get("service"):
                    issues.append(
                        ValidationIssue(
                            question_label,
                            f"document {document_id} does not match service filter",
                        )
                    )
                if metadata.get("environment") != filters.get("environment"):
                    issues.append(
                        ValidationIssue(
                            question_label,
                            f"document {document_id} does not match environment filter",
                        )
                    )
                if (
                    "incident_type" in filters
                    and metadata.get("incident_type") != filters["incident_type"]
                ):
                    issues.append(
                        ValidationIssue(
                            question_label,
                            f"document {document_id} does not match incident_type filter",
                        )
                    )

            # Historical evaluation must not use evidence outside its validity window.
            if as_of is not None:
                try:
                    valid_from = parse_date(metadata.get("valid_from"))
                    valid_until = (
                        parse_date(metadata.get("valid_until"))
                        if metadata.get("valid_until") is not None
                        else None
                    )
                except (TypeError, ValueError):
                    continue
                if valid_from > as_of.date() or (
                    valid_until is not None and as_of.date() > valid_until
                ):
                    issues.append(
                        ValidationIssue(
                            question_label,
                            f"document {document_id} is not valid at as_of",
                        )
                    )

    if query_ids != EXPECTED_QUERY_IDS:
        issues.append(ValidationIssue(label, "query IDs must be Q-001 through Q-012"))
