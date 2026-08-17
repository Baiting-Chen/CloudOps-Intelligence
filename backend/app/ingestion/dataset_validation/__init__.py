"""Public API for validating the controlled CloudOps Phase 0 dataset.

Callers should import from this module instead of depending on individual
validator modules. Keeping the public surface small lets the implementation be
refactored without changing ingestion code or tests.
"""

from .documents import discover_ingestible_incident_documents, load_document_metadata
from .models import ValidationContext, ValidationIssue
from .runner import DEFAULT_PROJECT_ROOT, main, validate_dataset

__all__ = [
    "DEFAULT_PROJECT_ROOT",
    "ValidationContext",
    "ValidationIssue",
    "discover_ingestible_incident_documents",
    "load_document_metadata",
    "main",
    "validate_dataset",
]
