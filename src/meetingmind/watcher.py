"""File watcher and processing orchestration."""

import asyncio
import signal
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from meetingmind.agents import analyze_transcript
from meetingmind.config import WatcherConfig
from meetingmind.markdown import generate_markdown, generate_output_filename
from meetingmind.state import StateStore


class TranscriptWatcher:
    """Watches a folder for new transcript files and processes them."""

    def __init__(self, config: WatcherConfig, state_store: StateStore):
        self.config = config
        self.state_store = state_store
        self._running = False
        self._shutdown_event = asyncio.Event()
        self._semaphore: asyncio.Semaphore | None = None

    def _setup_signal_handlers(self) -> None:
        """Setup graceful shutdown handlers."""
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._signal_handler)

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals."""
        print(f"\nReceived signal {signum}, initiating graceful shutdown...")
        self._running = False
        # Schedule the shutdown event to be set in the event loop
        if asyncio.get_event_loop().is_running():
            asyncio.get_event_loop().call_soon_threadsafe(self._shutdown_event.set)

    def _get_eligible_files(self) -> list[Path]:
        """Get list of files eligible for processing."""
        if not self.config.input_folder.exists():
            return []

        eligible = []
        for ext in self.config.file_extensions:
            pattern = f"*{ext}" if ext.startswith(".") else f"*.{ext}"
            for file_path in self.config.input_folder.glob(pattern):
                if file_path.is_file() and not self.state_store.is_processed(file_path):
                    eligible.append(file_path)

        return eligible

    def _is_file_stable(self, file_path: Path) -> bool:
        """
        Check if file is stable (not being written to).

        Returns True if file size hasn't changed after waiting.
        """
        try:
            size_before = file_path.stat().st_size
            time.sleep(self.config.stability_check_seconds)
            size_after = file_path.stat().st_size
            return size_before == size_after
        except OSError:
            return False

    async def _process_file(self, file_path: Path) -> None:
        """Process a single transcript file."""
        async with self._semaphore:
            try:
                print(f"Processing: {file_path.name}")

                # Check file stability
                if not await asyncio.to_thread(self._is_file_stable, file_path):
                    print(f"  Skipping (file not stable): {file_path.name}")
                    return

                # Read transcript
                transcript = await asyncio.to_thread(file_path.read_text, encoding="utf-8")

                # Analyze using manager-worker orchestration
                analysis = await analyze_transcript(transcript, file_path.name)

                # Generate markdown
                markdown_content = generate_markdown(analysis)

                # Determine output path
                output_filename = generate_output_filename(
                    self.config.filename_template, file_path, datetime.now()
                )
                output_path = self.config.output_folder / output_filename

                # Ensure output folder exists
                self.config.output_folder.mkdir(parents=True, exist_ok=True)

                # Write output
                await asyncio.to_thread(
                    output_path.write_text, markdown_content, encoding="utf-8"
                )

                # Mark as processed
                self.state_store.mark_processed(file_path, output_path)

                print(f"  ✓ Completed: {file_path.name} -> {output_filename}")

            except Exception as e:
                print(f"  ✗ Error processing {file_path.name}: {e}")
                # Don't mark as processed on error
                raise

    async def _process_batch(self, files: list[Path]) -> None:
        """Process a batch of files with bounded concurrency."""
        if not files:
            return

        print(f"Found {len(files)} new file(s) to process")

        tasks = [self._process_file(file_path) for file_path in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Report any errors
        errors = [r for r in results if isinstance(r, Exception)]
        if errors:
            print(f"Completed batch with {len(errors)} error(s)")

    async def watch(self) -> None:
        """Start watching for new transcript files."""
        self._running = True
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_files)
        self._setup_signal_handlers()

        print(f"Starting MeetingMind watcher")
        print(f"  Input folder: {self.config.input_folder.resolve()}")
        print(f"  Output folder: {self.config.output_folder.resolve()}")
        print(f"  Extensions: {', '.join(self.config.file_extensions)}")
        print(f"  Max concurrent: {self.config.max_concurrent_files}")
        print(f"  Poll interval: {self.config.poll_interval_seconds}s")
        print()

        # Ensure input folder exists
        self.config.input_folder.mkdir(parents=True, exist_ok=True)

        while self._running:
            try:
                # Find eligible files
                eligible_files = await asyncio.to_thread(self._get_eligible_files)

                # Process them
                if eligible_files:
                    await self._process_batch(eligible_files)

                # Wait for next poll or shutdown
                try:
                    await asyncio.wait_for(
                        self._shutdown_event.wait(), timeout=self.config.poll_interval_seconds
                    )
                    # If we got here, shutdown was triggered
                    break
                except asyncio.TimeoutError:
                    # Normal timeout, continue loop
                    pass

            except Exception as e:
                print(f"Error in watch loop: {e}")
                await asyncio.sleep(self.config.poll_interval_seconds)

        print("\nShutdown complete")

    async def process_once(self) -> int:
        """
        Process all eligible files once and exit.

        Returns the number of files processed.
        """
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_files)

        # Ensure folders exist
        self.config.input_folder.mkdir(parents=True, exist_ok=True)
        self.config.output_folder.mkdir(parents=True, exist_ok=True)

        # Find and process eligible files
        eligible_files = await asyncio.to_thread(self._get_eligible_files)

        if not eligible_files:
            print("No new files to process")
            return 0

        await self._process_batch(eligible_files)
        return len(eligible_files)
