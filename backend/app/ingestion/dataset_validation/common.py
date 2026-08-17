"""Low-level parsing and validation helpers for dataset validators.

Domain modules use these helpers to produce consistent diagnostics while
keeping file-format mechanics out of business-rule validation.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from .models import ValidationIssue


def load_json(path: Path) -> Any:
    """Read and decode one UTF-8 JSON file."""

    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def parse_datetime(value: Any) -> datetime:
    """Parse an RFC 3339 timestamp and normalize it to UTC."""

    if not isinstance(value, str):
        raise ValueError("must be an RFC 3339 string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("must include a timezone")
    return parsed.astimezone(timezone.utc)


def parse_date(value: Any) -> date:
    """Parse an ISO 8601 calendar date."""

    if not isinstance(value, str):
        raise ValueError("must be an ISO 8601 date string")
    return date.fromisoformat(value)


def is_enum_value(value: Any, allowed: set[str]) -> bool:
    """Return whether a value is a string in the allowed contract set."""

    return isinstance(value, str) and value in allowed


def require_exact_fields(
    value: Any,
    expected: set[str],
    label: str,
    issues: list[ValidationIssue],
) -> bool:
    """Require an object to contain exactly the expected field names.

    Exact matching is intentional: the controlled dataset should fail loudly
    when producers and consumers drift to different schema versions.
    """

    if not isinstance(value, dict):
        issues.append(ValidationIssue(label, "must be a JSON object"))
        return False

    actual = set(value)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        issues.append(ValidationIssue(label, f"missing fields: {', '.join(missing)}"))
    if extra:
        issues.append(ValidationIssue(label, f"unexpected fields: {', '.join(extra)}"))
    return not missing and not extra


def validate_unique_string_array(
    value: Any,
    field: str,
    label: str,
    issues: list[ValidationIssue],
    *,
    allow_empty: bool = True,
    pattern: re.Pattern[str] | None = None,
) -> bool:
    """Validate a list of unique strings and an optional identifier pattern."""

    if not isinstance(value, list):
        issues.append(ValidationIssue(label, f"{field} must be an array"))
        return False
    if not allow_empty and not value:
        issues.append(ValidationIssue(label, f"{field} must not be empty"))
        return False
    if not all(isinstance(item, str) and item for item in value):
        issues.append(ValidationIssue(label, f"{field} must contain non-empty strings"))
        return False
    if len(value) != len(set(value)):
        issues.append(ValidationIssue(label, f"{field} must not contain duplicates"))
        return False
    if pattern is not None and any(pattern.fullmatch(item) is None for item in value):
        issues.append(ValidationIssue(label, f"{field} contains an invalid identifier"))
        return False
    return True
