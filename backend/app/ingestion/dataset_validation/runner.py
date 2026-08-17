"""Orchestration and CLI reporting for Phase 0 dataset validation.

The runner composes independent domain validators and is the only module that
decides execution order or formats the final command-line report.
"""

from __future__ import annotations

from pathlib import Path

from .common import load_json
from .documents import discover_ingestible_incident_documents
from .incidents import validate_incident_packs
from .models import ValidationContext, ValidationIssue
from .questions import validate_questions
from .schemas import validate_schema_files
from .services import validate_service_definitions


DEFAULT_PROJECT_ROOT = Path(__file__).resolve().parents[4]


def _build_context(project_root: Path | None = None) -> ValidationContext:
    """Create a normalized validation context for production or test data."""

    selected_root = DEFAULT_PROJECT_ROOT if project_root is None else project_root
    return ValidationContext(project_root=selected_root.resolve())


def validate_dataset(project_root: Path | None = None) -> list[ValidationIssue]:
    """Run all Phase 0 validators and return every detected issue."""

    context = _build_context(project_root)
    issues: list[ValidationIssue] = []
    validate_schema_files(context, issues)
    validate_service_definitions(context, issues)
    documents = validate_incident_packs(context, issues)
    validate_questions(documents, context, issues)
    return issues


def main(project_root: Path | None = None) -> int:
    """Print a validation report and return a process-compatible exit code."""

    context = _build_context(project_root)
    issues = validate_dataset(context.project_root)
    if issues:
        print(f"Dataset validation failed with {len(issues)} issue(s):")
        for issue in issues:
            print(f"- {issue}")
        return 1

    service_count = len(list((context.dataset_root / "services").glob("*.json")))
    schema_count = len(list((context.dataset_root / "schemas").glob("*.schema.json")))
    incident_count = len(
        [path for path in context.incidents_root.glob("INC-*") if path.is_dir()]
    )
    document_count = len(discover_ingestible_incident_documents(context))
    question_count = len(load_json(context.dataset_root / "eval" / "questions.json")["questions"])

    print("Dataset validation passed:")
    print(f"- {service_count} service definitions")
    print(f"- {schema_count} schemas")
    print(f"- {incident_count} Incident Packs")
    print(f"- {document_count} ingestible documents")
    print(f"- {question_count} evaluation questions")
    return 0
