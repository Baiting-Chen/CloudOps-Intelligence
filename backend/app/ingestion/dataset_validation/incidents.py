"""Cross-file validation for Incident Packs and evaluation Ground Truth.

This module verifies pack completeness, document identity, and agreement
between evidence metadata and the evaluation-only incident record.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .common import (
    is_enum_value,
    load_json,
    parse_datetime,
    require_exact_fields,
    validate_unique_string_array,
)
from .contracts import (
    ENVIRONMENTS,
    EXPECTED_INCIDENTS,
    GROUND_TRUTH_FIELDS,
    INCIDENT_TYPES,
    NORMALIZED_LABEL_PATTERN,
    PACK_FILES,
    SERVICES,
)
from .documents import load_document_metadata, validate_metadata
from .models import DocumentRecord, ValidationContext, ValidationIssue


def _validate_ground_truth(
    truth: Any,
    truth_path: Path,
    incident_id: str,
    issues: list[ValidationIssue],
    context: ValidationContext,
) -> bool:
    """Validate Ground Truth structure and references within one pack."""

    label = context.relative(truth_path)
    if not require_exact_fields(truth, GROUND_TRUTH_FIELDS, label, issues):
        return False

    if truth["incident_id"] != incident_id:
        issues.append(ValidationIssue(label, "incident_id must match the directory name"))
    if not is_enum_value(truth["service"], SERVICES):
        issues.append(ValidationIssue(label, "service is outside the Phase 0 enum"))
    if not is_enum_value(truth["environment"], ENVIRONMENTS):
        issues.append(ValidationIssue(label, "environment is outside the Phase 0 enum"))
    if not is_enum_value(truth["incident_type"], INCIDENT_TYPES):
        issues.append(ValidationIssue(label, "incident_type is outside the Phase 0 enum"))
    try:
        parse_datetime(truth["occurred_at"])
    except (TypeError, ValueError) as exc:
        issues.append(ValidationIssue(label, f"invalid occurred_at: {exc}"))
    root_cause = truth["root_cause"]
    if not isinstance(root_cause, str) or NORMALIZED_LABEL_PATTERN.fullmatch(root_cause) is None:
        issues.append(ValidationIssue(label, "root_cause must be a normalized snake_case label"))

    relevant_valid = validate_unique_string_array(
        truth["relevant_documents"],
        "relevant_documents",
        label,
        issues,
        allow_empty=False,
    )
    if relevant_valid:
        for filename in truth["relevant_documents"]:
            referenced = truth_path.parent / filename
            if (
                filename == "ground-truth.json"
                or filename not in PACK_FILES
                or not referenced.is_file()
            ):
                issues.append(ValidationIssue(label, f"unresolvable relevant document: {filename}"))

    for field, allow_empty in (
        ("required_checks", False),
        ("optional_checks", True),
        ("unsafe_actions", False),
        ("misleading_signals", True),
    ):
        validate_unique_string_array(
            truth[field],
            field,
            label,
            issues,
            allow_empty=allow_empty,
            pattern=NORMALIZED_LABEL_PATTERN,
        )
    return True


def validate_incident_packs(
    context: ValidationContext,
    issues: list[ValidationIssue],
) -> dict[str, DocumentRecord]:
    """Validate every Incident Pack and return documents indexed by ID."""

    incident_dirs = sorted(path for path in context.incidents_root.glob("INC-*") if path.is_dir())
    actual_incidents = {path.name for path in incident_dirs}
    if actual_incidents != EXPECTED_INCIDENTS:
        issues.append(
            ValidationIssue(
                context.relative(context.incidents_root),
                "expected Incident Packs "
                f"{sorted(EXPECTED_INCIDENTS)}, got {sorted(actual_incidents)}",
            )
        )

    documents: dict[str, DocumentRecord] = {}
    for incident_dir in incident_dirs:
        incident_id = incident_dir.name
        label = context.relative(incident_dir)
        actual_files = {path.name for path in incident_dir.iterdir() if path.is_file()}
        if actual_files != PACK_FILES:
            issues.append(
                ValidationIssue(
                    label,
                    "pack files differ; "
                    f"missing={sorted(PACK_FILES - actual_files)}, "
                    f"extra={sorted(actual_files - PACK_FILES)}",
                )
            )

        truth_path = incident_dir / "ground-truth.json"
        truth: dict[str, Any] | None = None
        try:
            loaded_truth = load_json(truth_path)
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(ValidationIssue(context.relative(truth_path), f"invalid JSON: {exc}"))
        else:
            if _validate_ground_truth(
                loaded_truth,
                truth_path,
                incident_id,
                issues,
                context,
            ):
                truth = loaded_truth

        for path in sorted(incident_dir.iterdir()):
            if not path.is_file() or path.name == "ground-truth.json":
                continue
            if path.suffix not in {".json", ".md", ".txt"}:
                issues.append(
                    ValidationIssue(context.relative(path), "unsupported Incident Pack file type")
                )
                continue
            try:
                metadata = load_document_metadata(path)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                issues.append(ValidationIssue(context.relative(path), str(exc)))
                continue
            validate_metadata(metadata, path, context, issues)

            document_id = metadata.get("document_id")
            if isinstance(document_id, str):
                if document_id in documents:
                    previous = documents[document_id].path
                    issues.append(
                        ValidationIssue(
                            context.relative(path),
                            "duplicate document_id also used by "
                            f"{context.relative(previous)}",
                        )
                    )
                else:
                    documents[document_id] = DocumentRecord(path=path, metadata=metadata)

            if truth is not None:
                for field in (
                    "incident_id",
                    "service",
                    "environment",
                    "incident_type",
                    "occurred_at",
                ):
                    if metadata.get(field) != truth[field]:
                        issues.append(
                            ValidationIssue(
                                context.relative(path),
                                f"{field} must match ground-truth.json",
                            )
                        )
    return documents
