"""Regression tests for Phase 0 dataset validation.

The tests protect the real repository dataset and use temporary copies for
negative cases. This keeps failure-path coverage deterministic and prevents a
test interruption from leaving source data corrupted.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from backend.app.ingestion.dataset_validation import (
    ValidationContext,
    discover_ingestible_incident_documents,
    load_document_metadata,
    main,
    validate_dataset,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _copy_dataset(tmp_path: Path) -> Path:
    """Create an isolated project root containing a copy of the dataset."""

    temporary_project = tmp_path / "project"
    shutil.copytree(PROJECT_ROOT / "dataset", temporary_project / "dataset")
    return temporary_project


def _load_questions(project_root: Path) -> tuple[Path, dict[str, Any]]:
    """Return the copied question path and decoded payload for mutation tests."""

    questions_path = project_root / "dataset" / "eval" / "questions.json"
    payload = json.loads(questions_path.read_text(encoding="utf-8"))
    return questions_path, payload


def _write_questions(path: Path, payload: dict[str, Any]) -> None:
    """Persist a deliberately modified evaluation payload in a readable form."""

    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def test_repository_dataset_is_valid() -> None:
    """Require the committed Phase 0 dataset to pass every validator."""

    assert validate_dataset(PROJECT_ROOT) == []


def test_discovery_excludes_ground_truth() -> None:
    """Expose exactly the 15 evidence documents and no evaluation-only files."""

    context = ValidationContext(PROJECT_ROOT)
    documents = discover_ingestible_incident_documents(context)

    assert len(documents) == 15
    assert all(path.name != "ground-truth.json" for path in documents)


def test_ground_truth_cannot_be_loaded_for_ingestion() -> None:
    """Reject direct attempts to treat Ground Truth as knowledge evidence."""

    ground_truth = PROJECT_ROOT / "dataset" / "incidents" / "INC-001" / "ground-truth.json"

    with pytest.raises(ValueError, match="evaluation-only"):
        load_document_metadata(ground_truth)


def test_missing_question_field_is_reported(tmp_path: Path) -> None:
    """Report a precise issue when a question omits a required field."""

    temporary_project = _copy_dataset(tmp_path)
    questions_path, payload = _load_questions(temporary_project)
    payload["questions"][0].pop("filters")
    _write_questions(questions_path, payload)

    issues = validate_dataset(temporary_project)

    assert any(
        issue.path.endswith("questions.json#questions[0]")
        and issue.message == "missing fields: filters"
        for issue in issues
    )


def test_unknown_document_reference_is_reported(tmp_path: Path) -> None:
    """Reject evaluation questions that cite a nonexistent document ID."""

    temporary_project = _copy_dataset(tmp_path)
    questions_path, payload = _load_questions(temporary_project)
    payload["questions"][0]["relevant_documents"] = ["missing-document"]
    _write_questions(questions_path, payload)

    issues = validate_dataset(temporary_project)

    assert any(
        issue.message == "unknown relevant document_id: missing-document" for issue in issues
    )


def test_cli_returns_nonzero_for_invalid_dataset(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Return a failing process code and actionable output for CI consumers."""

    temporary_project = _copy_dataset(tmp_path)
    questions_path, payload = _load_questions(temporary_project)
    payload["questions"][0].pop("filters")
    _write_questions(questions_path, payload)

    exit_code = main(temporary_project)
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "Dataset validation failed" in output
    assert "missing fields: filters" in output
