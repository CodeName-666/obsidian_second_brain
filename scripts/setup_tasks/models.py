"""Shared data models for the structured second-brain setup."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SetupOptions:
    """Normalized options for one setup run."""

    tool_names: tuple[str, ...]
    home_paths: tuple[Path, ...]
    vault_root_path: Path
    task_names: tuple[str, ...]

