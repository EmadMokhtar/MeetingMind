"""Persistent state management for processed files."""

import json
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field


class ProcessedFileRecord(BaseModel):
    """Record of a processed file."""

    path: str = Field(..., description="Absolute path to the processed file")
    processed_at: datetime = Field(..., description="When the file was processed")
    output_path: str | None = Field(None, description="Path to the generated output file")


class ProcessedFilesState(BaseModel):
    """State tracking processed files."""

    version: int = Field(default=1, description="State format version")
    files: dict[str, ProcessedFileRecord] = Field(
        default_factory=dict, description="Map of file path to record"
    )


class StateStore:
    """Persistent store for processed files state."""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self._state: ProcessedFilesState | None = None

    def load(self) -> ProcessedFilesState:
        """Load state from disk."""
        if self._state is not None:
            return self._state

        if not self.state_file.exists():
            self._state = ProcessedFilesState()
            return self._state

        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)
            self._state = ProcessedFilesState.model_validate(data)
        except (json.JSONDecodeError, ValueError) as e:
            # Corrupted state file, start fresh
            print(f"Warning: corrupted state file ({e}), starting fresh")
            self._state = ProcessedFilesState()

        return self._state

    def save(self) -> None:
        """Save state to disk."""
        if self._state is None:
            return

        # Ensure parent directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Write atomically: write to temp file, then rename
        temp_file = self.state_file.with_suffix(".tmp")
        try:
            with open(temp_file, "w") as f:
                json.dump(self._state.model_dump(mode="json"), f, indent=2, default=str)
            temp_file.replace(self.state_file)
        except Exception as save_error:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception:
                pass  # Ignore cleanup errors to preserve original exception
            raise save_error

    def is_processed(self, file_path: Path) -> bool:
        """Check if a file has already been processed."""
        state = self.load()
        abs_path = str(file_path.resolve())
        return abs_path in state.files

    def mark_processed(
        self, file_path: Path, output_path: Path | None = None
    ) -> ProcessedFileRecord:
        """Mark a file as processed."""
        state = self.load()
        abs_path = str(file_path.resolve())

        record = ProcessedFileRecord(
            path=abs_path,
            processed_at=datetime.now(),
            output_path=str(output_path.resolve()) if output_path else None,
        )

        state.files[abs_path] = record
        self.save()

        return record

    def get_record(self, file_path: Path) -> ProcessedFileRecord | None:
        """Get the record for a processed file."""
        state = self.load()
        abs_path = str(file_path.resolve())
        return state.files.get(abs_path)

    def get_all_processed(self) -> list[ProcessedFileRecord]:
        """Get all processed file records."""
        state = self.load()
        return list(state.files.values())

    def clear(self) -> None:
        """Clear all state (useful for testing)."""
        self._state = ProcessedFilesState()
        if self.state_file.exists():
            self.state_file.unlink()
