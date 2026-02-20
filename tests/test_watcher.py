"""Test watcher functionality."""

import asyncio
import tempfile
from pathlib import Path

import pytest

from meetingmind.config import WatcherConfig
from meetingmind.state import StateStore
from meetingmind.watcher import TranscriptWatcher


@pytest.fixture
def temp_dirs():
    """Create temporary input and output directories."""
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        yield Path(input_dir), Path(output_dir)


@pytest.fixture
def temp_state_file():
    """Create a temporary state file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        state_file = Path(f.name)
    yield state_file
    if state_file.exists():
        state_file.unlink()


@pytest.fixture
def watcher_config(temp_dirs):
    """Create a test watcher configuration."""
    input_dir, output_dir = temp_dirs
    return WatcherConfig(
        input_folder=input_dir,
        output_folder=output_dir,
        file_extensions=[".txt", ".md"],
        poll_interval_seconds=1.0,
        stability_check_seconds=0.5,
        max_concurrent_files=2,
        filename_template="{source_stem}_{timestamp}.md",
    )


@pytest.fixture
def watcher(watcher_config, temp_state_file):
    """Create a TranscriptWatcher instance."""
    state_store = StateStore(temp_state_file)
    return TranscriptWatcher(watcher_config, state_store)


def test_watcher_init(watcher, watcher_config, subtests):
    """Test watcher initialization."""
    with subtests.test("config_set"):
        assert watcher.config == watcher_config

    with subtests.test("state_store_set"):
        assert watcher.state_store is not None

    with subtests.test("not_running_initially"):
        assert not watcher._running


def test_get_eligible_files_empty_folder(watcher, subtests):
    """Test getting eligible files from empty folder."""
    files = watcher._get_eligible_files()

    with subtests.test("no_files"):
        assert len(files) == 0


def test_get_eligible_files_with_txt_files(watcher, temp_dirs, subtests):
    """Test getting eligible .txt files."""
    input_dir, _ = temp_dirs

    # Create test files
    (input_dir / "test1.txt").write_text("Content 1")
    (input_dir / "test2.txt").write_text("Content 2")
    (input_dir / "test.log").write_text("Not eligible")

    files = watcher._get_eligible_files()

    with subtests.test("correct_count"):
        assert len(files) == 2

    with subtests.test("only_txt_files"):
        assert all(f.suffix == ".txt" for f in files)


def test_get_eligible_files_with_md_files(watcher, temp_dirs, subtests):
    """Test getting eligible .md files."""
    input_dir, _ = temp_dirs

    (input_dir / "notes.md").write_text("Notes")
    (input_dir / "readme.md").write_text("Readme")

    files = watcher._get_eligible_files()

    with subtests.test("finds_md_files"):
        assert len(files) == 2


def test_get_eligible_files_excludes_processed(watcher, temp_dirs, temp_state_file, subtests):
    """Test that processed files are excluded."""
    input_dir, _ = temp_dirs

    file1 = input_dir / "test1.txt"
    file2 = input_dir / "test2.txt"

    file1.write_text("Content 1")
    file2.write_text("Content 2")

    # Mark file1 as processed
    watcher.state_store.mark_processed(file1)

    files = watcher._get_eligible_files()

    with subtests.test("only_unprocessed"):
        assert len(files) == 1

    with subtests.test("correct_file"):
        assert files[0] == file2


def test_is_file_stable(watcher, temp_dirs, subtests):
    """Test file stability check."""
    input_dir, _ = temp_dirs
    test_file = input_dir / "test.txt"
    test_file.write_text("Content")

    with subtests.test("stable_file"):
        assert watcher._is_file_stable(test_file)


def test_is_file_stable_nonexistent(watcher, temp_dirs, subtests):
    """Test stability check for nonexistent file."""
    input_dir, _ = temp_dirs
    test_file = input_dir / "nonexistent.txt"

    with subtests.test("nonexistent_not_stable"):
        assert not watcher._is_file_stable(test_file)


@pytest.mark.asyncio
async def test_process_once_no_files(watcher, subtests):
    """Test process_once with no files."""
    count = await watcher.process_once()

    with subtests.test("zero_files_processed"):
        assert count == 0


def test_watcher_config_filename_template(subtests):
    """Test different filename templates."""
    templates = [
        "{source_stem}_{timestamp}.md",
        "report_{source_stem}.md",
        "{timestamp}_{source_stem}.md",
    ]

    for template in templates:
        with subtests.test(template=template):
            config = WatcherConfig(filename_template=template)
            assert config.filename_template == template


def test_watcher_config_max_concurrent(subtests):
    """Test max concurrent files configuration."""
    config = WatcherConfig(max_concurrent_files=5)

    with subtests.test("custom_max_concurrent"):
        assert config.max_concurrent_files == 5


def test_watcher_config_extensions(subtests):
    """Test file extensions configuration."""
    config = WatcherConfig(file_extensions=[".txt", ".md", ".log"])

    with subtests.test("custom_extensions"):
        assert len(config.file_extensions) == 3
        assert ".log" in config.file_extensions
