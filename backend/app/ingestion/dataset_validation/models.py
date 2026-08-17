"""Core data structures used by the dataset validation pipeline.

The context object makes filesystem dependencies explicit, which allows tests
to validate isolated dataset copies without mutating the repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ValidationIssue:
    """Describe one actionable dataset problem and its source location."""

    path: str
    message: str

    def __str__(self) -> str:
        """Render the issue in a stable, human-readable CLI format."""

        return f"{self.path}: {self.message}"


@dataclass(frozen=True)
class ValidationContext:
    """Hold repository paths for one independent validation run."""

    project_root: Path

    @property
    def dataset_root(self) -> Path:
        """Return the dataset directory below the selected project root."""

        return self.project_root / "dataset"

    @property
    def incidents_root(self) -> Path:
        """Return the Incident Pack directory for this validation run."""

        return self.dataset_root / "incidents"

    def relative(self, path: Path) -> str:
        """Return a stable project-relative path for diagnostics."""

        try:
            return path.relative_to(self.project_root).as_posix()
        except ValueError:
            return path.as_posix()


@dataclass(frozen=True)
class DocumentRecord:
    """Associate a validated document path with its parsed metadata."""

    path: Path
    metadata: dict[str, Any]
