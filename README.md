# MeetingMind

Intelligent transcript processor with AI-powered insights using manager-worker agent orchestration.

## Features

- 🔍 **Automatic transcript discovery** - Continuously monitors folder for new transcript files
- 🤖 **AI-powered analysis** - Uses Pydantic AI with manager-worker orchestration to extract insights
- 📊 **Comprehensive extraction** - Generates summaries, action points, todos, important mentions, recaps, tone analysis, and key insights
- 💾 **Persistent state** - Tracks processed files across restarts
- ⚡ **Parallel processing** - Handles multiple transcripts concurrently with bounded concurrency
- 🎨 **Beautiful markdown output** - Generates well-formatted analysis documents
- ⚙️ **Configurable** - Customizable paths, templates, and processing settings

## Documentation

| Document | Audience | Description |
|----------|----------|-------------|
| [User Manual](docs/user-manual.md) | End users | Getting started, configuration, workflows, troubleshooting, FAQ |
| [Technical Reference](docs/technical-reference.md) | Developers | Architecture, data models, agent system, API reference, development guide |

## Installation

```bash
# Install dependencies
make install

# Or using uv directly
uv pip install -e ".[dev]"
```

## Quick Start

### Watch Mode (Continuous)

Monitor a folder and automatically process new transcripts:

```bash
# Use default settings
make run

# Or with custom options
meetingmind watch --input-folder ./transcripts --output-folder ./outputs
```

### Process Mode (One-time)

Process all unprocessed files once and exit:

```bash
meetingmind process --input-folder ./transcripts
```

### Check Status

View processing history and statistics:

```bash
meetingmind status
```

### Reset State

Clear all processing history:

```bash
meetingmind reset
```

## 🐳 Docker

MeetingMind provides a production-ready Docker image with multi-stage builds for optimal size and security.

### Build

Basic build:

```bash
docker build -t meetingmind:latest .
```

Build with metadata (recommended for CI/CD):

```bash
docker build \
  --build-arg GIT_SHA=$(git rev-parse --short HEAD) \
  --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  -t meetingmind:latest .
```

### Run: Watch Mode (Continuous Monitoring)

The primary use case — continuously monitor a folder and process new transcripts:

```bash
docker run -d \
  --name meetingmind-watcher \
  -v $(pwd)/transcripts:/app/transcripts \
  -v $(pwd)/outputs:/app/output \
  -e MEETINGMIND_API_KEY=your-api-key-here \
  meetingmind:latest
```

**What this does:**
- Runs in detached mode (`-d`)
- Mounts local `./transcripts` folder (input files)
- Mounts local `./outputs` folder (generated analyses)
- Injects your API key at runtime (never baked into image)
- Starts `meetingmind watch` by default

View logs:
```bash
docker logs -f meetingmind-watcher
```

Stop the watcher:
```bash
docker stop meetingmind-watcher
```

### Run: One-Time Process

Process a single file and exit:

```bash
docker run --rm \
  -v $(pwd)/transcripts:/app/transcripts \
  -v $(pwd)/outputs:/app/output \
  -e MEETINGMIND_API_KEY=your-api-key-here \
  meetingmind:latest \
  process --input /app/transcripts/meeting.txt
```

Process all unprocessed files once:

```bash
docker run --rm \
  -v $(pwd)/transcripts:/app/transcripts \
  -v $(pwd)/outputs:/app/output \
  -e MEETINGMIND_API_KEY=your-api-key-here \
  meetingmind:latest \
  process --input-folder /app/transcripts
```

### Run: Other Commands

Check processing status:

```bash
docker run --rm \
  -v $(pwd)/transcripts:/app/transcripts \
  -v $(pwd)/outputs:/app/output \
  meetingmind:latest \
  status
```

Reset processing state:

```bash
docker run --rm \
  -v $(pwd)/transcripts:/app/transcripts \
  -v $(pwd)/outputs:/app/output \
  meetingmind:latest \
  reset
```

### Configuration via Environment Variables

Pass any configuration using `-e` flags:

| Variable | Default | Description |
|----------|---------|-------------|
| `MEETINGMIND_INPUT_FOLDER` | `./transcripts` | Input folder for transcript files |
| `MEETINGMIND_OUTPUT_FOLDER` | `./outputs` | Output folder for generated analyses |
| `MEETINGMIND_FILE_EXTENSIONS` | `.txt,.md` | Comma-separated file extensions to monitor |
| `MEETINGMIND_MAX_CONCURRENT_FILES` | `3` | Max files to process concurrently (1-10) |
| `MEETINGMIND_POLL_INTERVAL_SECONDS` | `5.0` | How often to check for new files (seconds) |
| `MEETINGMIND_STABILITY_CHECK_SECONDS` | `2.0` | Wait time to ensure file is fully written |
| `MEETINGMIND_FILENAME_TEMPLATE` | `{source_stem}_{timestamp}.md` | Output filename pattern |
| `MEETINGMIND_STATE_FILE` | `.meetingmind_state.json` | State file location |
| `MEETINGMIND_MODEL_PROVIDER` | `openai` | AI provider (`openai`, `anthropic`, or `test`) |
| `MEETINGMIND_MODEL_NAME` | `gpt-4` | Model to use for analysis |
| `MEETINGMIND_API_KEY` | *(required)* | Your AI provider API key |

Example with custom configuration:

```bash
docker run -d \
  --name meetingmind-watcher \
  -v $(pwd)/transcripts:/app/transcripts \
  -v $(pwd)/outputs:/app/output \
  -e MEETINGMIND_API_KEY=your-api-key-here \
  -e MEETINGMIND_MODEL_PROVIDER=anthropic \
  -e MEETINGMIND_MODEL_NAME=claude-3-opus-20240229 \
  -e MEETINGMIND_MAX_CONCURRENT_FILES=5 \
  -e MEETINGMIND_POLL_INTERVAL_SECONDS=10.0 \
  meetingmind:latest
```

### Using an `.env` File

For cleaner commands, use an `.env` file:

Create `.env`:
```bash
MEETINGMIND_API_KEY=your-api-key-here
MEETINGMIND_MODEL_PROVIDER=openai
MEETINGMIND_MODEL_NAME=gpt-4
MEETINGMIND_MAX_CONCURRENT_FILES=5
```

Run with `--env-file`:
```bash
docker run -d \
  --name meetingmind-watcher \
  -v $(pwd)/transcripts:/app/transcripts \
  -v $(pwd)/outputs:/app/output \
  --env-file .env \
  meetingmind:latest
```

### Docker Notes

- **Volume mounts are required** - The container needs access to your transcript files and somewhere to write output
- **API keys at runtime only** - Never baked into the image for security
- **Non-root user** - Runs as UID 1001 for enhanced security
- **State persistence** - The `.meetingmind_state.json` file is stored in the mounted `/app/transcripts` directory
- **Graceful shutdown** - Container handles `SIGTERM` cleanly, allowing in-progress files to complete

## Configuration

Configure via environment variables or `.env` file:

```bash
# Folders
MEETINGMIND_INPUT_FOLDER=./transcripts
MEETINGMIND_OUTPUT_FOLDER=./outputs

# File types to monitor (.txt,.md by default)
MEETINGMIND_FILE_EXTENSIONS=.txt,.md

# Processing settings
MEETINGMIND_MAX_CONCURRENT_FILES=3
MEETINGMIND_POLL_INTERVAL_SECONDS=5.0
MEETINGMIND_STABILITY_CHECK_SECONDS=2.0

# Output filename template
# Placeholders: {source_stem}, {timestamp}
MEETINGMIND_FILENAME_TEMPLATE={source_stem}_{timestamp}.md

# State file location
MEETINGMIND_STATE_FILE=.meetingmind_state.json

# Model configuration
MEETINGMIND_MODEL_PROVIDER=openai
MEETINGMIND_MODEL_NAME=gpt-4
MEETINGMIND_API_KEY=your-api-key-here
```

## Output Format

Each transcript generates a markdown file with these sections:

- 📋 **Summary** - Concise overview with key topics
- ✅ **Action Points** - Prioritized tasks with owners and deadlines
- 📝 **Todo List** - Tasks to be completed
- 👥 **Important Mentions** - Significant people/entities mentioned
- 🔄 **Recap** - Highlights, decisions, and next steps
- 🎭 **Meeting Tone** - Sentiment and collaboration analysis
- 💡 **Key Insights** - Strategic insights and recommendations

## Architecture

### Manager-Worker Orchestration

MeetingMind uses Pydantic AI's manager-worker pattern:

- **Manager Agent** - Orchestrates the analysis workflow
- **Worker Agents** - Specialized extractors for each insight type:
  - Summary Agent
  - Action Points Agent
  - Todo List Agent
  - Important Mentions Agent
  - Recap Agent
  - Meeting Tone Agent
  - Key Insights Agent

The manager delegates tasks to workers and aggregates results into a comprehensive analysis.

### Key Components

```
src/meetingmind/
├── config.py       # Configuration management
├── models.py       # Pydantic models for structured outputs
├── agents.py       # Manager and worker agents
├── state.py        # Persistent state tracking
├── markdown.py     # Markdown generation
├── watcher.py      # File watching and orchestration
└── main.py         # CLI entry point
```

## Development

### Run Tests

```bash
# Run all tests
make test

# Run specific test file
uv run pytest tests/test_agents.py -v

# Run with coverage
uv run pytest tests/ --cov=meetingmind --cov-report=html
```

### Code Quality

```bash
# Format code
make format

# Run linter
make lint

# Run pre-commit hooks
pre-commit run --all-files
```

### Project Structure

```
MeetingMind/
├── src/meetingmind/     # Source code
├── tests/               # Test suite
├── pyproject.toml       # Project configuration
├── Makefile            # Build commands
└── README.md           # This file
```

## How It Works

1. **File Discovery** - Watcher periodically scans input folder for eligible files
2. **Stability Check** - Ensures files are completely written before processing
3. **State Check** - Skips files already processed (persisted across restarts)
4. **Parallel Processing** - Processes multiple files concurrently (bounded by `max_concurrent_files`)
5. **AI Analysis** - Manager agent orchestrates worker agents to extract insights
6. **Markdown Generation** - Creates formatted output document
7. **State Update** - Marks file as processed and saves state

## Error Handling

- Files that fail processing are **not** marked as processed
- Errors are logged but don't stop the watcher
- Corrupted state files are detected and reset automatically
- File stability checks prevent reading partial files

## Performance

- **Bounded Concurrency** - Process multiple transcripts in parallel (default: 3)
- **Efficient State Tracking** - Fast lookups for already-processed files
- **Atomic State Writes** - Prevents corruption on crash/interrupt
- **Graceful Shutdown** - Handles SIGTERM/SIGINT cleanly

## Requirements

- Python 3.11+
- OpenAI API key (for default model)
- Dependencies managed via `pyproject.toml`

## License

See LICENSE file for details.

## Contributing

Contributions welcome! Please:

1. Run tests: `make test`
2. Format code: `make format`
3. Ensure linting passes: `make lint`
4. Write tests for new features

## Support

For issues or questions, please open a GitHub issue.
