"""Backward-compatible CLI entry point for Phase 0 dataset validation.

Implementation lives in ``dataset_validation`` so this module remains a small,
stable command target for developers and future CI jobs.
"""

from __future__ import annotations

from pathlib import Path

from .dataset_validation import (
    DEFAULT_PROJECT_ROOT,
    ValidationContext,
    ValidationIssue,
    discover_ingestible_incident_documents as _discover_documents,
    load_document_metadata,
    main,
    validate_dataset,
)


PROJECT_ROOT = DEFAULT_PROJECT_ROOT
DATASET_ROOT = PROJECT_ROOT / "dataset"
INCIDENTS_ROOT = DATASET_ROOT / "incidents"


def discover_ingestible_incident_documents(
    project_root: Path | None = None,
) -> list[Path]:
    """Discover evidence documents using the default or supplied project root."""

    selected_root = PROJECT_ROOT if project_root is None else project_root.resolve()
    return _discover_documents(ValidationContext(selected_root))


__all__ = [
    "DATASET_ROOT",
    "INCIDENTS_ROOT",
    "PROJECT_ROOT",
    "ValidationIssue",
    "discover_ingestible_incident_documents",
    "load_document_metadata",
    "main",
    "validate_dataset",
]


if __name__ == "__main__":
    raise SystemExit(main())
