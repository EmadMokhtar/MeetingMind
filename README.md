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
