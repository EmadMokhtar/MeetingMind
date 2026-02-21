# syntax=docker/dockerfile:1
# ─────────────────────────────────────────────────────────────────────────────
# MeetingMind — Production-ready Docker image
# ─────────────────────────────────────────────────────────────────────────────
# Usage:
#   docker build -t meetingmind:latest .
#   docker run -v ./transcripts:/app/transcripts \
#              -v ./output:/app/output \
#              -e OPENAI_API_KEY=sk-... \
#              meetingmind:latest watch
#
# Override the default command:
#   docker run ... meetingmind:latest process --input /app/transcripts/meeting.txt
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: builder — install dependencies with uv
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Install uv (official installer — pinned version for reproducibility)
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy only the dependency manifests first (maximises cache reuse)
COPY pyproject.toml uv.lock ./

# Install production dependencies into a local .venv
# --frozen  → fail if uv.lock is out of date (never silently update)
# --no-dev  → skip dev/test dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: runtime — slim production image
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL org.opencontainers.image.title="MeetingMind" \
      org.opencontainers.image.description="Intelligent transcript processor with AI-powered insights" \
      org.opencontainers.image.source="https://github.com/emadmokhtar/meetingmind" \
      org.opencontainers.image.licenses="MIT"

# Create a non-root user with an explicit UID/GID
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-log-init --no-create-home appuser

WORKDIR /app

# Copy the pre-built virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application source (after deps — keep this layer last for fast rebuilds)
COPY src/ ./src/
COPY pyproject.toml ./

# Make the venv's Python and scripts the default
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create volume mount points for input/output
# These directories should be mounted from the host at runtime
VOLUME ["/app/transcripts"]
VOLUME ["/app/output"]

# Switch to non-root user before running anything
USER appuser

# Exec-form ENTRYPOINT + CMD allows users to override subcommands easily
# Default: meetingmind watch
# Override: docker run meetingmind:latest process --input /app/transcripts/meeting.txt
ENTRYPOINT ["meetingmind"]
CMD ["watch"]
