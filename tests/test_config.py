"""Test configuration module."""

import os
from pathlib import Path

import pytest

from meetingmind.config import ModelProvider, Settings, WatcherConfig


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
        assert config.filename_template == "{meeting_timestamp}_{source_stem}.md"


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


def test_watcher_config_invalid_poll_interval(subtests):
    """Test WatcherConfig validation for invalid poll_interval_seconds."""
    from pydantic import ValidationError

    with subtests.test("poll_interval_too_low"):
        with pytest.raises(ValidationError, match="greater than or equal to 1"):
            WatcherConfig(poll_interval_seconds=0.5)


def test_watcher_config_invalid_stability_check(subtests):
    """Test WatcherConfig validation for invalid stability_check_seconds."""
    from pydantic import ValidationError

    with subtests.test("stability_check_too_low"):
        with pytest.raises(ValidationError, match="greater than or equal to 0.5"):
            WatcherConfig(stability_check_seconds=0.3)


def test_watcher_config_invalid_max_concurrent_low(subtests):
    """Test WatcherConfig validation when max_concurrent_files < 1."""
    from pydantic import ValidationError

    with subtests.test("max_concurrent_too_low"):
        with pytest.raises(ValidationError, match="greater than or equal to 1"):
            WatcherConfig(max_concurrent_files=0)


def test_watcher_config_invalid_max_concurrent_high(subtests):
    """Test WatcherConfig validation when max_concurrent_files > 10."""
    from pydantic import ValidationError

    with subtests.test("max_concurrent_too_high"):
        with pytest.raises(ValidationError, match="less than or equal to 10"):
            WatcherConfig(max_concurrent_files=11)


def test_get_watcher_config_empty_extensions(subtests):
    """Test get_watcher_config raises ValueError when MEETINGMIND_FILE_EXTENSIONS is empty."""
    with subtests.test("empty_string"):
        settings = Settings(file_extensions="")
        with pytest.raises(ValueError, match="At least one file extension must be specified"):
            settings.get_watcher_config()

    with subtests.test("whitespace_only"):
        settings = Settings(file_extensions="   ")
        with pytest.raises(ValueError, match="At least one file extension must be specified"):
            settings.get_watcher_config()

    with subtests.test("only_commas"):
        settings = Settings(file_extensions=",,,")
        with pytest.raises(ValueError, match="At least one file extension must be specified"):
            settings.get_watcher_config()


def test_model_provider_when_openai_then_equals_string_openai(subtests):
    """Test ModelProvider enum values are strings."""
    with subtests.test("openai_value"):
        assert ModelProvider.OPENAI == "openai"

    with subtests.test("anthropic_value"):
        assert ModelProvider.ANTHROPIC == "anthropic"

    with subtests.test("azure_value"):
        assert ModelProvider.AZURE == "azure"

    with subtests.test("test_value"):
        assert ModelProvider.TEST == "test"

    with subtests.test("string_inheritance"):
        # ModelProvider inherits from str
        assert isinstance(ModelProvider.OPENAI, str)
        assert isinstance(ModelProvider.ANTHROPIC, str)
        assert isinstance(ModelProvider.AZURE, str)


def test_model_provider_when_string_env_var_then_parses_correctly(subtests):
    """Test Settings parses string env var to ModelProvider enum."""
    # Test with different environment variable values
    with subtests.test("openai_string"):
        # Save original value if exists
        original = os.environ.get("MEETINGMIND_MODEL_PROVIDER")
        try:
            os.environ["MEETINGMIND_MODEL_PROVIDER"] = "openai"
            settings = Settings()
            assert settings.model_provider == ModelProvider.OPENAI
        finally:
            # Restore or remove
            if original is not None:
                os.environ["MEETINGMIND_MODEL_PROVIDER"] = original
            else:
                os.environ.pop("MEETINGMIND_MODEL_PROVIDER", None)

    with subtests.test("anthropic_string"):
        original = os.environ.get("MEETINGMIND_MODEL_PROVIDER")
        try:
            os.environ["MEETINGMIND_MODEL_PROVIDER"] = "anthropic"
            settings = Settings()
            assert settings.model_provider == ModelProvider.ANTHROPIC
        finally:
            if original is not None:
                os.environ["MEETINGMIND_MODEL_PROVIDER"] = original
            else:
                os.environ.pop("MEETINGMIND_MODEL_PROVIDER", None)

    with subtests.test("test_string"):
        original = os.environ.get("MEETINGMIND_MODEL_PROVIDER")
        try:
            os.environ["MEETINGMIND_MODEL_PROVIDER"] = "test"
            settings = Settings()
            assert settings.model_provider == ModelProvider.TEST
        finally:
            if original is not None:
                os.environ["MEETINGMIND_MODEL_PROVIDER"] = original
            else:
                os.environ.pop("MEETINGMIND_MODEL_PROVIDER", None)

    with subtests.test("azure_string"):
        original = os.environ.get("MEETINGMIND_MODEL_PROVIDER")
        try:
            os.environ["MEETINGMIND_MODEL_PROVIDER"] = "azure"
            settings = Settings()
            assert settings.model_provider == ModelProvider.AZURE
        finally:
            if original is not None:
                os.environ["MEETINGMIND_MODEL_PROVIDER"] = original
            else:
                os.environ.pop("MEETINGMIND_MODEL_PROVIDER", None)


def test_settings_when_extra_env_var_then_allows_unknown_field(subtests):
    """Test Settings allows unknown environment variables with extra='allow'."""
    original_unknown = os.environ.get("MEETINGMIND_UNKNOWN_VAR")
    original_another = os.environ.get("MEETINGMIND_ANOTHER_UNKNOWN")

    try:
        os.environ["MEETINGMIND_UNKNOWN_VAR"] = "some_value"
        os.environ["MEETINGMIND_ANOTHER_UNKNOWN"] = "another_value"

        # Should not raise ValidationError
        with subtests.test("creates_successfully"):
            settings = Settings()
            assert settings is not None

        with subtests.test("has_known_fields"):
            # Known fields should still work
            assert hasattr(settings, "model_provider")
            assert hasattr(settings, "input_folder")

        with subtests.test("extra_fields_accessible"):
            # Extra fields should be accessible if stored
            # Note: With extra='allow', they might be stored as model_extra
            # but Settings should not raise during initialization
            assert settings.model_provider == ModelProvider.OPENAI  # default

    finally:
        # Restore original values
        if original_unknown is not None:
            os.environ["MEETINGMIND_UNKNOWN_VAR"] = original_unknown
        else:
            os.environ.pop("MEETINGMIND_UNKNOWN_VAR", None)

        if original_another is not None:
            os.environ["MEETINGMIND_ANOTHER_UNKNOWN"] = original_another
        else:
            os.environ.pop("MEETINGMIND_ANOTHER_UNKNOWN", None)
