"""Observability configuration for MeetingMind.

Provides structured logging setup using structlog.
"""

import logging

import structlog


def configure_logging() -> None:
    """Configure structlog for the application.

    Sets up structured logging with ISO timestamps and console renderer.
    Should be called once at application startup before any logging occurs.
    """
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
