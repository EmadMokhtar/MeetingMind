"""Test state persistence."""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from meetingmind.state import StateStore


@pytest.fixture
def temp_state_file():
    """Create a temporary state file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        state_file = Path(f.name)
    yield state_file
    if state_file.exists():
        state_file.unlink()


def test_state_store_init_no_file(temp_state_file, subtests):
    """Test StateStore initialization with no existing file."""
    store = StateStore(temp_state_file)
    state = store.load()

    with subtests.test("version"):
        assert state.version == 1

    with subtests.test("files_empty"):
        assert len(state.files) == 0


def test_state_store_mark_processed(temp_state_file, subtests):
    """Test marking a file as processed."""
    store = StateStore(temp_state_file)

    file_path = Path("/tmp/test.txt")
    output_path = Path("/tmp/output.md")

    record = store.mark_processed(file_path, output_path)

    with subtests.test("record_path"):
        assert record.path == str(file_path.resolve())

    with subtests.test("record_output_path"):
        assert record.output_path == str(output_path.resolve())

    with subtests.test("record_timestamp"):
        assert isinstance(record.processed_at, datetime)


def test_state_store_is_processed(temp_state_file, subtests):
    """Test checking if file is processed."""
    store = StateStore(temp_state_file)
    file_path = Path("/tmp/test.txt")

    with subtests.test("not_processed_initially"):
        assert not store.is_processed(file_path)

    store.mark_processed(file_path)

    with subtests.test("processed_after_marking"):
        assert store.is_processed(file_path)


def test_state_store_get_record(temp_state_file, subtests):
    """Test retrieving a specific record."""
    store = StateStore(temp_state_file)
    file_path = Path("/tmp/test.txt")

    with subtests.test("no_record_initially"):
        assert store.get_record(file_path) is None

    store.mark_processed(file_path)
    record = store.get_record(file_path)

    with subtests.test("record_exists"):
        assert record is not None

    with subtests.test("record_path_matches"):
        assert record.path == str(file_path.resolve())


def test_state_store_get_all_processed(temp_state_file, subtests):
    """Test getting all processed records."""
    store = StateStore(temp_state_file)

    file1 = Path("/tmp/test1.txt")
    file2 = Path("/tmp/test2.txt")

    store.mark_processed(file1)
    store.mark_processed(file2)

    records = store.get_all_processed()

    with subtests.test("count"):
        assert len(records) == 2

    with subtests.test("contains_file1"):
        paths = [r.path for r in records]
        assert str(file1.resolve()) in paths

    with subtests.test("contains_file2"):
        paths = [r.path for r in records]
        assert str(file2.resolve()) in paths


def test_state_store_persistence(temp_state_file, subtests):
    """Test state persists across instances."""
    file_path = Path("/tmp/test.txt")

    # First instance
    store1 = StateStore(temp_state_file)
    store1.mark_processed(file_path)

    # Second instance
    store2 = StateStore(temp_state_file)

    with subtests.test("file_still_processed"):
        assert store2.is_processed(file_path)

    records = store2.get_all_processed()

    with subtests.test("records_persisted"):
        assert len(records) == 1


def test_state_store_atomic_write(temp_state_file, subtests):
    """Test atomic write doesn't corrupt existing data on error."""
    store = StateStore(temp_state_file)

    # Write initial data
    file1 = Path("/tmp/test1.txt")
    store.mark_processed(file1)

    # Verify file exists and is valid JSON
    with subtests.test("initial_state_valid"):
        assert temp_state_file.exists()
        with open(temp_state_file) as f:
            data = json.load(f)
            assert "files" in data


def test_state_store_clear(temp_state_file, subtests):
    """Test clearing all state."""
    store = StateStore(temp_state_file)

    file_path = Path("/tmp/test.txt")
    store.mark_processed(file_path)

    with subtests.test("processed_before_clear"):
        assert store.is_processed(file_path)

    store.clear()

    with subtests.test("not_processed_after_clear"):
        assert not store.is_processed(file_path)

    with subtests.test("state_file_removed"):
        assert not temp_state_file.exists()


def test_state_store_corrupted_file(temp_state_file, subtests):
    """Test handling of corrupted state file."""
    # Write invalid JSON
    temp_state_file.write_text("{ invalid json }")

    store = StateStore(temp_state_file)
    state = store.load()

    with subtests.test("loads_fresh_state"):
        assert len(state.files) == 0

    with subtests.test("version_is_default"):
        assert state.version == 1
