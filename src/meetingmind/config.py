"""Configuration management for MeetingMind."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class WatcherConfig(BaseModel):
    """Configuration for the file watcher."""

    input_folder: Path = Field(default=Path("./transcripts"))
    output_folder: Path = Field(default=Path("./outputs"))
    file_extensions: list[str] = Field(default=[".txt", ".md"])
    poll_interval_seconds: float = Field(default=5.0, ge=1.0)
    stability_check_seconds: float = Field(default=2.0, ge=0.5)
    max_concurrent_files: int = Field(default=3, ge=1, le=10)
    filename_template: str = Field(default="{source_stem}_{timestamp}.md")


class Settings(BaseSettings):
    """Application settings.

    Attributes:
        input_folder: Directory to watch for transcript files
        output_folder: Directory where processed files are saved
        file_extensions: Comma-separated list of file extensions to watch
        poll_interval_seconds: How often to check for new files (seconds)
        stability_check_seconds: Time to wait for file stability (seconds)
        max_concurrent_files: Maximum number of files to process concurrently
        filename_template: Template for output filenames (supports {source_stem}, {timestamp})
        state_file: Path to state persistence file
        model_provider: AI model provider (openai, anthropic, or test)
        model_name: Name of the AI model to use
        api_key: API key for the model provider (stored securely)
    """

    model_config = SettingsConfigDict(
        env_prefix="MEETINGMIND_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Watcher configuration
    input_folder: Path = Field(default=Path("./transcripts"))
    output_folder: Path = Field(default=Path("./outputs"))
    file_extensions: str = Field(default=".txt,.md")
    poll_interval_seconds: float = Field(default=5.0)
    stability_check_seconds: float = Field(default=2.0)
    max_concurrent_files: int = Field(default=3)
    filename_template: str = Field(default="{source_stem}_{timestamp}.md")

    # State persistence
    state_file: Path = Field(default=Path(".meetingmind_state.json"))

    # Model configuration
    model_provider: Literal["openai", "anthropic", "test"] = Field(default="openai")
    model_name: str = Field(default="gpt-4")
    api_key: SecretStr | None = Field(default=None)

    def get_api_key(self) -> str | None:
        """Get the API key value.

        Returns:
            The API key as a plain string, or None if not set.
        """
        return self.api_key.get_secret_value() if self.api_key else None

    def get_watcher_config(self) -> WatcherConfig:
        """Convert settings to watcher config."""
        extensions = [ext.strip() for ext in self.file_extensions.split(",") if ext.strip()]
        if not extensions:
            raise ValueError("At least one file extension must be specified in MEETINGMIND_FILE_EXTENSIONS")
        return WatcherConfig(
            input_folder=self.input_folder,
            output_folder=self.output_folder,
            file_extensions=extensions,
            poll_interval_seconds=self.poll_interval_seconds,
            stability_check_seconds=self.stability_check_seconds,
            max_concurrent_files=self.max_concurrent_files,
            filename_template=self.filename_template,
        )


def load_settings() -> Settings:
    """Load application settings from environment and .env file."""
    return Settings()


# Module-level singleton for convenient access
settings = Settings()
