"""File watcher and processing orchestration."""

import asyncio
import signal
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog

from meetingmind.agents import analyze_transcript
from meetingmind.config import WatcherConfig
from meetingmind.markdown import generate_markdown, generate_output_filename
from meetingmind.state import StateStore

logger = structlog.get_logger(__name__)


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
        logger.info("signal_received", signal=signum, action="graceful_shutdown")
        self._running = False
        try:
            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(self._shutdown_event.set)
        except RuntimeError:
            pass  # No running loop

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

    async def _is_file_stable(self, file_path: Path) -> bool:
        """
        Check if file is stable (not being written to).

        Returns True if file size hasn't changed after waiting.
        """
        try:
            size_before = file_path.stat().st_size
            await asyncio.sleep(self.config.stability_check_seconds)
            size_after = file_path.stat().st_size
            return size_before == size_after
        except OSError:
            return False

    async def _process_file(self, file_path: Path) -> None:
        """Process a single transcript file."""
        assert self._semaphore is not None, "_semaphore must be initialized before processing"
        async with self._semaphore:
            try:
                logger.info("processing_file", file=file_path.name)

                # Check file stability
                if not await self._is_file_stable(file_path):
                    logger.info("file_not_stable", file=file_path.name, action="skipped")
                    return

                # Read transcript
                transcript = await asyncio.to_thread(file_path.read_text, encoding="utf-8")

                # Analyze using manager-worker orchestration
                analysis = await analyze_transcript(transcript, file_path.name)

                # Generate markdown
                markdown_content = generate_markdown(analysis)

                # Determine output path
                meeting_dt = analysis.metadata.meeting_datetime if analysis.metadata else None
                output_filename = generate_output_filename(
                    self.config.filename_template, file_path, datetime.now(), meeting_dt
                )
                output_path = self.config.output_folder / output_filename

                # Ensure output folder exists
                self.config.output_folder.mkdir(parents=True, exist_ok=True)

                # Write output
                await asyncio.to_thread(output_path.write_text, markdown_content, encoding="utf-8")

                # Mark as processed
                self.state_store.mark_processed(file_path, output_path)

                logger.info(
                    "file_completed",
                    source=file_path.name,
                    output=output_filename,
                    status="success",
                )

            except Exception as e:
                logger.error("file_processing_error", file=file_path.name, error=str(e))
                # Don't mark as processed on error
                raise

    async def _process_batch(self, files: list[Path]) -> None:
        """Process a batch of files with bounded concurrency."""
        if not files:
            return

        logger.info("batch_found", file_count=len(files))

        tasks = [self._process_file(file_path) for file_path in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Report any errors
        errors = [(files[i], r) for i, r in enumerate(results) if isinstance(r, Exception)]
        if errors:
            logger.warning("batch_completed_with_errors", error_count=len(errors))
            for file_path, error in errors:
                logger.error("batch_error_detail", file=file_path.name, error=str(error))

    async def watch(self) -> None:
        """Start watching for new transcript files."""
        self._running = True
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_files)
        self._setup_signal_handlers()

        logger.info(
            "watcher_starting",
            input_folder=str(self.config.input_folder.resolve()),
            output_folder=str(self.config.output_folder.resolve()),
            extensions=", ".join(self.config.file_extensions),
            max_concurrent=self.config.max_concurrent_files,
            poll_interval=self.config.poll_interval_seconds,
        )

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
                logger.error("watch_loop_error", error=str(e))
                await asyncio.sleep(self.config.poll_interval_seconds)

        logger.info("watcher_shutdown_complete")

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
            logger.info("no_new_files")
            return 0

        logger.info("batch_found", file_count=len(eligible_files))

        tasks = [self._process_file(file_path) for file_path in eligible_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successfully processed files
        success_count = sum(1 for r in results if not isinstance(r, Exception))

        # Report any errors
        errors = [(eligible_files[i], r) for i, r in enumerate(results) if isinstance(r, Exception)]
        if errors:
            logger.warning("batch_completed_with_errors", error_count=len(errors))
            for file_path, error in errors:
                logger.error("batch_error_detail", file=file_path.name, error=str(error))

        return success_count

    async def process_single_file(self, file_path: Path) -> None:
        """
        Process a single transcript file directly by path.

        Args:
            file_path: Path to the transcript file to process.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file extension is not in the configured list.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Transcript file not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        expected_extensions = [
            ext if ext.startswith(".") else f".{ext}" for ext in self.config.file_extensions
        ]
        if file_path.suffix not in expected_extensions:
            raise ValueError(
                f"File extension '{file_path.suffix}' not in configured extensions: "
                f"{self.config.file_extensions}"
            )

        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_files)

        # Ensure output folder exists
        self.config.output_folder.mkdir(parents=True, exist_ok=True)

        await self._process_file(file_path)
