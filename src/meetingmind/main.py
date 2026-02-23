"""CLI entry point for MeetingMind."""

import asyncio
import logging
import sys
from pathlib import Path

import click
import structlog

from meetingmind.config import load_settings
from meetingmind.state import StateStore
from meetingmind.watcher import TranscriptWatcher

logger = structlog.get_logger(__name__)


def _configure_logging() -> None:
    """Configure structlog for the application."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )


@click.group()
@click.version_option()
def cli():
    """MeetingMind - Intelligent transcript processor with AI-powered insights."""
    _configure_logging()


@cli.command()
@click.option(
    "--input-folder",
    type=click.Path(path_type=Path),
    help="Folder to watch for transcript files",
)
@click.option(
    "--output-folder",
    type=click.Path(path_type=Path),
    help="Folder to write analysis markdown files",
)
@click.option(
    "--poll-interval",
    type=float,
    help="Seconds between folder checks",
)
@click.option(
    "--max-concurrent",
    type=int,
    help="Maximum files to process concurrently",
)
def watch(
    input_folder: Path | None,
    output_folder: Path | None,
    poll_interval: float | None,
    max_concurrent: int | None,
):
    """Watch a folder for new transcript files and process them continuously."""
    # Load settings
    settings = load_settings()

    # Override with CLI options
    if input_folder is not None:
        settings.input_folder = input_folder
    if output_folder is not None:
        settings.output_folder = output_folder
    if poll_interval is not None:
        settings.poll_interval_seconds = poll_interval
    if max_concurrent is not None:
        settings.max_concurrent_files = max_concurrent

    # Create watcher
    config = settings.get_watcher_config()
    state_store = StateStore(settings.state_file)
    watcher = TranscriptWatcher(config, state_store)

    # Run watcher
    try:
        asyncio.run(watcher.watch())
    except KeyboardInterrupt:
        logger.info("interrupted_by_user")
        sys.exit(0)


@cli.command()
@click.option(
    "--input-folder",
    type=click.Path(path_type=Path),
    help="Folder to scan for transcript files",
)
@click.option(
    "--output-folder",
    type=click.Path(path_type=Path),
    help="Folder to write analysis markdown files",
)
@click.option(
    "--max-concurrent",
    type=int,
    help="Maximum files to process concurrently",
)
def process(
    input_folder: Path | None,
    output_folder: Path | None,
    max_concurrent: int | None,
):
    """Process all unprocessed transcript files once and exit."""
    # Load settings
    settings = load_settings()

    # Override with CLI options
    if input_folder is not None:
        settings.input_folder = input_folder
    if output_folder is not None:
        settings.output_folder = output_folder
    if max_concurrent is not None:
        settings.max_concurrent_files = max_concurrent

    # Create watcher
    config = settings.get_watcher_config()
    state_store = StateStore(settings.state_file)
    watcher = TranscriptWatcher(config, state_store)

    # Process once
    try:
        count = asyncio.run(watcher.process_once())
        logger.info("processing_complete", files_processed=count)
    except KeyboardInterrupt:
        logger.info("interrupted_by_user")
        sys.exit(1)


@cli.command()
def status():
    """Show processing status and statistics."""
    settings = load_settings()
    state_store = StateStore(settings.state_file)

    records = state_store.get_all_processed()

    if not records:
        logger.info("no_files_processed")
        return

    logger.info("files_processed_total", count=len(records))
    logger.info("recent_files_header")

    # Sort by processed_at descending
    sorted_records = sorted(records, key=lambda r: r.processed_at, reverse=True)

    for record in sorted_records[:10]:
        path = Path(record.path)
        logger.info(
            "file_record",
            filename=path.name,
            processed_at=record.processed_at.strftime("%Y-%m-%d %H:%M:%S"),
            output=Path(record.output_path).name if record.output_path else None,
        )


@cli.command()
@click.confirmation_option(prompt="This will clear all processing history. Continue?")
def reset():
    """Reset processing state (clear all history)."""
    settings = load_settings()
    state_store = StateStore(settings.state_file)
    state_store.clear()
    logger.info("state_reset")


if __name__ == "__main__":
    cli()
