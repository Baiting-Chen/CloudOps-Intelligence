"""Document loading, discovery, and metadata validation.

This module owns the ingestion boundary for Markdown, TXT, and JSON evidence.
Ground Truth is rejected here so no future caller can accidentally add it to
the searchable knowledge base.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .common import is_enum_value, load_json, parse_date, parse_datetime, require_exact_fields
from .contracts import (
    DOCUMENT_ID_PATTERN,
    DOCUMENT_TYPES,
    ENVIRONMENTS,
    INCIDENT_ID_PATTERN,
    INCIDENT_TYPES,
    KEBAB_CASE_PATTERN,
    METADATA_FIELDS,
    SERVICES,
    SEVERITIES,
)
from .models import ValidationContext, ValidationIssue


def _load_front_matter(path: Path) -> dict[str, Any]:
    """Read JSON-compatible front matter from a text document."""

    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        raise ValueError("missing opening JSON-compatible front matter delimiter")

    try:
        closing_index = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing closing front matter delimiter") from exc

    raw_metadata = "\n".join(lines[1:closing_index]).strip()
    metadata = json.loads(raw_metadata)
    if not isinstance(metadata, dict):
        raise ValueError("front matter must be a JSON object")
    if not any(line.strip() for line in lines[closing_index + 1 :]):
        raise ValueError("document body must not be empty")
    return metadata


def load_document_metadata(path: Path) -> dict[str, Any]:
    """Load metadata from one supported, ingestible incident document."""

    # Ground Truth exists only to score retrieval and generation behavior.
    if path.name == "ground-truth.json":
        raise ValueError("ground truth is evaluation-only and must not be ingested")
    if path.suffix == ".json":
        payload = load_json(path)
        if not isinstance(payload, dict) or not isinstance(payload.get("metadata"), dict):
            raise ValueError("JSON document must contain an object-valued metadata field")
        return payload["metadata"]
    if path.suffix in {".md", ".txt"}:
        return _load_front_matter(path)
    raise ValueError(f"unsupported document extension: {path.suffix}")


def discover_ingestible_incident_documents(context: ValidationContext) -> list[Path]:
    """Return supported Incident Pack evidence, excluding Ground Truth."""

    return sorted(
        path
        for path in context.incidents_root.glob("INC-*/*")
        if path.is_file()
        and path.name != "ground-truth.json"
        and path.suffix in {".json", ".md", ".txt"}
    )


def validate_metadata(
    metadata: dict[str, Any],
    path: Path,
    context: ValidationContext,
    issues: list[ValidationIssue],
) -> None:
    """Validate document metadata fields, formats, and source identity."""

    label = context.relative(path)
    if not require_exact_fields(metadata, METADATA_FIELDS, label, issues):
        return

    document_id = metadata["document_id"]
    if not isinstance(document_id, str) or DOCUMENT_ID_PATTERN.fullmatch(document_id) is None:
        issues.append(ValidationIssue(label, "document_id has an invalid format"))
    if not is_enum_value(metadata["document_type"], DOCUMENT_TYPES):
        issues.append(ValidationIssue(label, "document_type is outside the Phase 0 enum"))
    incident_id = metadata["incident_id"]
    if incident_id is not None and (
        not isinstance(incident_id, str) or INCIDENT_ID_PATTERN.fullmatch(incident_id) is None
    ):
        issues.append(ValidationIssue(label, "incident_id has an invalid format"))
    if not is_enum_value(metadata["service"], SERVICES):
        issues.append(ValidationIssue(label, "service is outside the Phase 0 enum"))
    if not is_enum_value(metadata["environment"], ENVIRONMENTS):
        issues.append(ValidationIssue(label, "environment is outside the Phase 0 enum"))
    if not is_enum_value(metadata["incident_type"], INCIDENT_TYPES):
        issues.append(ValidationIssue(label, "incident_type is outside the Phase 0 enum"))
    if not is_enum_value(metadata["severity"], SEVERITIES):
        issues.append(ValidationIssue(label, "severity is outside the Phase 0 enum"))

    version = metadata["version"]
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        issues.append(ValidationIssue(label, "version must be a positive integer"))
    access_scope = metadata["access_scope"]
    if not isinstance(access_scope, str) or KEBAB_CASE_PATTERN.fullmatch(access_scope) is None:
        issues.append(ValidationIssue(label, "access_scope must be a kebab-case identifier"))
    if not isinstance(metadata["section"], str) or not metadata["section"].strip():
        issues.append(ValidationIssue(label, "section must be a non-empty string"))
    if metadata["source_path"] != label:
        issues.append(
            ValidationIssue(
                label,
                f"source_path must point to this file, got {metadata['source_path']!r}",
            )
        )

    try:
        parse_datetime(metadata["occurred_at"])
    except (TypeError, ValueError) as exc:
        issues.append(ValidationIssue(label, f"invalid occurred_at: {exc}"))
    try:
        valid_from = parse_date(metadata["valid_from"])
        if metadata["valid_until"] is not None:
            valid_until = parse_date(metadata["valid_until"])
            if valid_until < valid_from:
                issues.append(ValidationIssue(label, "valid_until precedes valid_from"))
    except (TypeError, ValueError) as exc:
        issues.append(ValidationIssue(label, f"invalid validity range: {exc}"))
