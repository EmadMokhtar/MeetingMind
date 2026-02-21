"""CLI entry point for MeetingMind."""

import asyncio
import sys
from pathlib import Path

import click

from meetingmind.config import load_settings
from meetingmind.state import StateStore
from meetingmind.watcher import TranscriptWatcher


@click.group()
@click.version_option()
def cli():
    """MeetingMind - Intelligent transcript processor with AI-powered insights."""
    pass


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
        print("\nInterrupted by user")
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
        print(f"\nProcessed {count} file(s)")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)


@cli.command()
def status():
    """Show processing status and statistics."""
    settings = load_settings()
    state_store = StateStore(settings.state_file)

    records = state_store.get_all_processed()

    if not records:
        print("No files have been processed yet")
        return

    print(f"Total files processed: {len(records)}")
    print("\nRecent files:")

    # Sort by processed_at descending
    sorted_records = sorted(records, key=lambda r: r.processed_at, reverse=True)

    for record in sorted_records[:10]:
        path = Path(record.path)
        print(f"  • {path.name}")
        print(f"    Processed: {record.processed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if record.output_path:
            print(f"    Output: {Path(record.output_path).name}")


@cli.command()
@click.confirmation_option(prompt="This will clear all processing history. Continue?")
def reset():
    """Reset processing state (clear all history)."""
    settings = load_settings()
    state_store = StateStore(settings.state_file)
    state_store.clear()
    print("Processing state has been reset")


if __name__ == "__main__":
    cli()
