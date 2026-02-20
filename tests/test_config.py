"""Test configuration module."""

import tempfile
from pathlib import Path

import pytest

from meetingmind.config import Settings, WatcherConfig, load_settings


def test_watcher_config_defaults(subtests):
    """Test WatcherConfig has sensible defaults."""
    config = WatcherConfig()

    with subtests.test("input_folder"):
        assert config.input_folder == Path("./transcripts")

    with subtests.test("output_folder"):
        assert config.output_folder == Path("./outputs")

    with subtests.test("file_extensions"):
        assert config.file_extensions == [".txt", ".md"]

    with subtests.test("poll_interval"):
        assert config.poll_interval_seconds == 5.0

    with subtests.test("stability_check"):
        assert config.stability_check_seconds == 2.0

    with subtests.test("max_concurrent"):
        assert config.max_concurrent_files == 3

    with subtests.test("filename_template"):
        assert config.filename_template == "{source_stem}_{timestamp}.md"


def test_settings_defaults(subtests):
    """Test Settings has correct defaults."""
    settings = Settings()

    with subtests.test("input_folder"):
        assert settings.input_folder == Path("./transcripts")

    with subtests.test("output_folder"):
        assert settings.output_folder == Path("./outputs")

    with subtests.test("file_extensions"):
        assert settings.file_extensions == ".txt,.md"

    with subtests.test("state_file"):
        assert settings.state_file == Path(".meetingmind_state.json")

    with subtests.test("model_provider"):
        assert settings.model_provider == "openai"


def test_settings_to_watcher_config(subtests):
    """Test conversion from Settings to WatcherConfig."""
    settings = Settings(
        input_folder=Path("/tmp/in"),
        output_folder=Path("/tmp/out"),
        file_extensions=".txt,.md,.log",
        max_concurrent_files=5,
    )

    config = settings.get_watcher_config()

    with subtests.test("input_folder"):
        assert config.input_folder == Path("/tmp/in")

    with subtests.test("output_folder"):
        assert config.output_folder == Path("/tmp/out")

    with subtests.test("file_extensions"):
        assert config.file_extensions == [".txt", ".md", ".log"]

    with subtests.test("max_concurrent"):
        assert config.max_concurrent_files == 5


def test_settings_custom_template():
    """Test custom filename template in settings."""
    settings = Settings(filename_template="report_{source_stem}.md")

    config = settings.get_watcher_config()

    assert config.filename_template == "report_{source_stem}.md"
