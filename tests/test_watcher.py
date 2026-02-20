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


@pytest.mark.asyncio
async def test_is_file_stable(watcher, temp_dirs, subtests):
    """Test file stability check."""
    input_dir, _ = temp_dirs
    test_file = input_dir / "test.txt"
    test_file.write_text("Content")

    with subtests.test("stable_file"):
        assert await watcher._is_file_stable(test_file)


@pytest.mark.asyncio
async def test_is_file_stable_nonexistent(watcher, temp_dirs, subtests):
    """Test stability check for nonexistent file."""
    input_dir, _ = temp_dirs
    test_file = input_dir / "nonexistent.txt"

    with subtests.test("nonexistent_not_stable"):
        assert not await watcher._is_file_stable(test_file)


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


@pytest.mark.asyncio
async def test_process_single_file_not_found(watcher, temp_dirs, subtests):
    """Test process_single_file raises FileNotFoundError for missing file."""
    input_dir, _ = temp_dirs
    non_existent = input_dir / "missing.txt"

    with subtests.test("raises_file_not_found"):
        with pytest.raises(FileNotFoundError, match="Transcript file not found"):
            await watcher.process_single_file(non_existent)


@pytest.mark.asyncio
async def test_process_single_file_not_a_file(watcher, temp_dirs, subtests):
    """Test process_single_file raises ValueError for a directory path."""
    input_dir, _ = temp_dirs
    subdir = input_dir / "subdir"
    subdir.mkdir()

    with subtests.test("raises_value_error"):
        with pytest.raises(ValueError, match="Path is not a file"):
            await watcher.process_single_file(subdir)


@pytest.mark.asyncio
async def test_process_single_file_wrong_extension(watcher, temp_dirs, subtests):
    """Test process_single_file raises ValueError for unsupported extension."""
    input_dir, _ = temp_dirs
    csv_file = input_dir / "data.csv"
    csv_file.write_text("col1,col2\nval1,val2")

    with subtests.test("raises_value_error"):
        with pytest.raises(ValueError, match="File extension '.csv' not in configured extensions"):
            await watcher.process_single_file(csv_file)


@pytest.mark.asyncio
async def test_process_single_file_success(watcher, temp_dirs, subtests, monkeypatch):
    """Test process_single_file processes a valid .txt file successfully."""
    from datetime import datetime
    from unittest.mock import AsyncMock, Mock

    from meetingmind.models import (
        ActionPoints,
        ImportantMentions,
        KeyInsights,
        MeetingTone,
        Recap,
        Summary,
        TodoList,
        TranscriptAnalysis,
    )

    input_dir, output_dir = temp_dirs
    test_file = input_dir / "meeting.txt"
    test_file.write_text("This is a test meeting transcript.")

    # Create mock analysis result
    mock_analysis = TranscriptAnalysis(
        source_file="meeting.txt",
        processed_at=datetime(2024, 1, 15, 10, 30),
        summary=Summary(content="Test summary", key_topics=["Topic 1"]),
        action_points=ActionPoints(items=[]),
        todo_list=TodoList(items=[]),
        important_mentions=ImportantMentions(items=[]),
        recap=Recap(),
        meeting_tone=MeetingTone(),
        key_insights=KeyInsights(),
    )

    # Mock the analyze_transcript function
    mock_analyze = AsyncMock(return_value=mock_analysis)
    monkeypatch.setattr("meetingmind.watcher.analyze_transcript", mock_analyze)

    # Mock generate_markdown to return simple string
    mock_generate_markdown = Mock(return_value="# Test Output\n\nContent here")
    monkeypatch.setattr("meetingmind.watcher.generate_markdown", mock_generate_markdown)

    # Mock generate_output_filename
    mock_generate_filename = Mock(return_value="meeting_20240115.md")
    monkeypatch.setattr("meetingmind.watcher.generate_output_filename", mock_generate_filename)

    # Process the file
    await watcher.process_single_file(test_file)

    with subtests.test("analyze_called"):
        assert mock_analyze.called

    with subtests.test("markdown_generated"):
        assert mock_generate_markdown.called

    with subtests.test("output_file_created"):
        output_file = output_dir / "meeting_20240115.md"
        assert output_file.exists()

    with subtests.test("output_content_correct"):
        output_file = output_dir / "meeting_20240115.md"
        assert "Test Output" in output_file.read_text()
