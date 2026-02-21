# MeetingMind — Technical Reference

## 1. Overview

MeetingMind is an intelligent transcript processor that automatically analyzes meeting transcripts and generates comprehensive, structured reports using AI-powered insights. It solves the time-consuming problem of manually reviewing meeting transcripts, extracting action items, and documenting key decisions.

The system watches a designated folder for new transcript files, processes them through a sophisticated multi-agent AI system that extracts different aspects in parallel (summaries, action items, todos, important mentions, recaps, tone analysis, and strategic insights), and generates well-formatted markdown reports. MeetingMind uses a manager-worker orchestration pattern where a manager agent coordinates seven specialized worker agents to analyze transcripts efficiently and comprehensively.

### Technology Stack

| Component | Technology | Version/Details |
|-----------|-----------|-----------------|
| **Language** | Python | 3.11+ |
| **CLI Framework** | Click | 8.1.0+ |
| **AI Framework** | Pydantic AI | 0.0.14+ |
| **Configuration** | Pydantic Settings | 2.0.0+ |
| **State Management** | JSON + Pydantic Models | Atomic writes with temp files |
| **Testing** | pytest + pytest-asyncio | 7.4.0+, 0.21.0+ |
| **Linting** | Ruff | 0.1.0+ |
| **Concurrency** | asyncio | Semaphore-bounded parallelism |

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         MeetingMind System                        │
└──────────────────────────────────────────────────────────────────┘

    File System                     Core Pipeline                Output
┌───────────────┐              ┌──────────────────┐         ┌─────────────┐
│  transcripts/ │──────────────▶│ TranscriptWatcher│─────────▶│  outputs/   │
│   *.txt       │   Monitor    │    (watcher.py)  │ Write   │   *.md      │
│   *.md        │              └──────────────────┘         └─────────────┘
└───────────────┘                       │
                                        │ Orchestrates
                                        ▼
                            ┌──────────────────────┐
                            │  analyze_transcript  │
                            │     (agents.py)      │
                            └──────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
            ┌───────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
            │ Manager Agent│◀───┤7 Worker Tools│───▶│Worker Agents│
            │  Aggregates  │    │  (Proxies)   │    │(7 Specialists)
            └──────────────┘    └──────────────┘    └─────────────┘
                    │
                    │ Returns TranscriptAnalysis
                    ▼
          ┌────────────────────┐
          │ generate_markdown  │
          │   (markdown.py)    │
          └────────────────────┘

┌──────────────────────┐              ┌────────────────────┐
│   StateStore         │              │   Settings         │
│   (state.py)         │              │   (config.py)      │
│  Tracks processed    │              │  Configuration     │
│  files in JSON       │              │  management        │
└──────────────────────┘              └────────────────────┘
```

## 2. Architecture

### 2.1 Module Map

| Module | Class/Function | Responsibility |
|--------|----------------|----------------|
| `config.py` | `Settings` | Application configuration with environment variable support |
| `config.py` | `WatcherConfig` | File watcher-specific configuration |
| `config.py` | `load_settings()` | Factory function to load settings |
| `models.py` | `Summary`, `ActionPoints`, etc. | Pydantic models for structured analysis output |
| `models.py` | `TranscriptAnalysis` | Root aggregation model containing all analysis results |
| `models.py` | `ProcessedFileRecord` | State tracking for individual processed files |
| `agents.py` | `_LazyAgent` | Lazy-initialization proxy for Agent instances |
| `agents.py` | `ManagerContext` | Dependency injection context for manager agent |
| `agents.py` | `analyze_transcript()` | Main orchestration function coordinating manager agent |
| `agents.py` | `summary_agent`, `action_points_agent`, etc. | 7 specialized worker agents (lazy proxies) |
| `agents.py` | `manager_agent` | Orchestrator agent that calls workers via tools |
| `watcher.py` | `TranscriptWatcher` | File monitoring and processing orchestration |
| `state.py` | `StateStore` | Persistent state management with atomic writes |
| `markdown.py` | `generate_markdown()` | Converts TranscriptAnalysis to formatted markdown |
| `markdown.py` | `generate_output_filename()` | Template-based filename generation |
| `main.py` | `cli()` | Click CLI group for all commands |
| `main.py` | `watch()`, `process()`, `status()`, `reset()` | CLI command implementations |

### 2.2 Data Flow

```
File System (*.txt, *.md)
        │
        ▼
[TranscriptWatcher._get_eligible_files()]
        │ Filters unprocessed files
        ▼
[TranscriptWatcher._is_file_stable()]
        │ Waits for file write completion
        ▼
[TranscriptWatcher._process_file()]
        │ Reads file content
        ▼
[analyze_transcript()] ──────────────────────────────────┐
        │                                                 │
        ▼                                                 │
[manager_agent.run()] ────┐                              │
        │                 │ Manager calls 7 tools        │
        │                 │ in parallel via LLM          │
        │                 ▼                              │
        │         Tool execution:                        │
        │         • get_summary()                        │
        │         • get_action_points()                  │
        │         • get_todo_list()                      │
        │         • get_important_mentions()             │
        │         • get_recap()                          │
        │         • get_meeting_tone()                   │
        │         • get_key_insights()                   │
        │                 │                              │
        │                 │ Each tool calls              │
        │                 │ respective worker agent      │
        │                 ▼                              │
        │         [worker_agent.run()]                   │
        │                 │                              │
        │                 ▼                              │
        │         Returns structured                     │
        │         Pydantic model                         │
        │                 │                              │
        │◀────────────────┘                              │
        │                                                 │
        ▼                                                 │
[TranscriptAnalysis object] ◀────────────────────────────┘
        │
        ▼
[generate_markdown()]
        │ Formats to markdown string
        ▼
[Write to output file]
        │
        ▼
[StateStore.mark_processed()]
        │ Persist processing record
        ▼
[Output: {source_stem}_{timestamp}.md]
```

### 2.3 Component Interactions

**Entry Point (main.py)**  
The CLI commands (`watch`, `process`, `status`, `reset`) are the user-facing entry points. Each command loads settings from environment variables and `.env` files, instantiates a `StateStore` and `TranscriptWatcher`, then executes the appropriate operation.

**Configuration Layer (config.py)**  
- `Settings` loads from environment variables with `MEETINGMIND_` prefix or from `.env` file
- CLI options override environment/file settings
- `get_watcher_config()` transforms Settings into WatcherConfig, splitting comma-separated file extensions

**Watching and Orchestration (watcher.py)**  
- `TranscriptWatcher` continuously polls the input folder at intervals
- `_get_eligible_files()` finds files matching extensions that haven't been processed (checked via StateStore)
- `_is_file_stable()` waits and compares file size to avoid processing incomplete files
- `_process_batch()` launches multiple `_process_file()` coroutines with `asyncio.gather()` and bounded concurrency via semaphore
- Each `_process_file()` calls `analyze_transcript()`, then `generate_markdown()`, writes output, and marks processed

**Agent System (agents.py)**  
- `analyze_transcript()` creates a `ManagerContext` with transcript text and filename
- Calls `manager_agent.run()` with a prompt instructing it to use all worker tools
- The manager agent is a `_LazyAgent` that lazily initializes the underlying `Agent` on first use
- Worker tools are registered via `_register_manager_tools()` callback when the manager agent initializes
- Each tool (e.g., `get_summary()`) calls the corresponding worker agent (e.g., `summary_agent.run()`)
- Worker agents are also `_LazyAgent` instances configured with specific `result_type` and `system_prompt`
- Results from all workers are aggregated into a `TranscriptAnalysis` object

**State Management (state.py)**  
- `StateStore` loads/saves a JSON file with processed file records
- Uses atomic writes: write to `.tmp` file, then `replace()` to avoid corruption
- `is_processed()` checks if a file's absolute path exists in state
- `mark_processed()` adds/updates record and immediately saves to disk

**Output Generation (markdown.py)**  
- `generate_markdown()` takes a `TranscriptAnalysis` and formats it into sections with emoji headers
- Priority emojis (🔴 🟡 🟢) for action points
- Section headers with emojis (📋 ✅ 📝 👥 🔄 🎭 💡)
- `generate_output_filename()` replaces `{source_stem}` and `{timestamp}` placeholders in template

### 2.4 Manager-Worker Agent Pattern

MeetingMind uses a **manager-worker orchestration pattern** implemented with Pydantic AI agents. This pattern enables parallel processing of different analysis aspects while maintaining type safety and structured outputs.

**Lazy Agent Proxies**  
All agents are wrapped in `_LazyAgent` proxies that defer actual `Agent` initialization until first use. This avoids requiring API keys during import/configuration and enables easy testing with mock models via the `override()` context manager.

**Manager Context Dependencies**  
The manager agent receives a `ManagerContext` containing the transcript text and source filename. This context is passed as `deps` when calling `manager_agent.run()` and is available to all registered tools via `RunContext[ManagerContext]`.

**Seven Worker Tools**  
When the manager agent is first initialized, the `_register_manager_tools()` callback registers 7 tools decorated with `@agent.tool`:

1. `get_summary()` → returns `Summary`
2. `get_action_points()` → returns `ActionPoints`
3. `get_todo_list()` → returns `TodoList`
4. `get_important_mentions()` → returns `ImportantMentions`
5. `get_recap()` → returns `Recap`
6. `get_meeting_tone()` → returns `MeetingTone`
7. `get_key_insights()` → returns `KeyInsights`

Each tool calls the corresponding worker agent's `.run()` method with the transcript from context and returns the structured Pydantic model output.

**Aggregation into TranscriptAnalysis**  
The manager agent's `result_type` is `TranscriptAnalysis`, which contains fields for all 7 worker outputs. The LLM (via Pydantic AI) automatically:
- Determines which tools to call based on the prompt
- Executes tool calls (potentially in parallel)
- Aggregates tool outputs into a `TranscriptAnalysis` instance
- Ensures type correctness via Pydantic validation

This pattern provides:
- **Separation of concerns**: Each worker specializes in one analysis type
- **Parallel execution**: Workers can run concurrently
- **Type safety**: All outputs validated by Pydantic
- **Testability**: Easy to override with test models
- **Lazy loading**: API keys only needed when actually running agents

## 3. Configuration Reference

### 3.1 Settings Fields

| Field | Env Variable | Type | Default | Constraints | Description |
|-------|--------------|------|---------|-------------|-------------|
| `input_folder` | `MEETINGMIND_INPUT_FOLDER` | `Path` | `./transcripts` | Must be valid path | Directory to watch for transcript files |
| `output_folder` | `MEETINGMIND_OUTPUT_FOLDER` | `Path` | `./outputs` | Must be valid path | Directory where processed markdown files are saved |
| `file_extensions` | `MEETINGMIND_FILE_EXTENSIONS` | `str` | `.txt,.md` | Comma-separated list | File extensions to watch (comma-separated) |
| `poll_interval_seconds` | `MEETINGMIND_POLL_INTERVAL_SECONDS` | `float` | `5.0` | >= 1.0 | How often to check for new files (seconds) |
| `stability_check_seconds` | `MEETINGMIND_STABILITY_CHECK_SECONDS` | `float` | `2.0` | >= 0.5 | Time to wait before checking if file is stable (seconds) |
| `max_concurrent_files` | `MEETINGMIND_MAX_CONCURRENT_FILES` | `int` | `3` | >= 1, <= 10 | Maximum number of files to process concurrently |
| `filename_template` | `MEETINGMIND_FILENAME_TEMPLATE` | `str` | `{source_stem}_{timestamp}.md` | Valid template string | Template for output filenames (supports `{source_stem}`, `{timestamp}`) |
| `state_file` | `MEETINGMIND_STATE_FILE` | `Path` | `.meetingmind_state.json` | Must be valid path | Path to state persistence file |
| `model_provider` | `MEETINGMIND_MODEL_PROVIDER` | `Literal["openai", "anthropic", "test"]` | `openai` | Must be one of the literal values | AI model provider |
| `model_name` | `MEETINGMIND_MODEL_NAME` | `str` | `gpt-4` | Non-empty string | Name of the AI model to use |
| `api_key` | `MEETINGMIND_API_KEY` | `SecretStr \| None` | `None` | Securely stored | API key for the model provider |

**Notes:**
- Environment variables use the `MEETINGMIND_` prefix
- Settings are loaded from `.env` file if present
- Case-insensitive matching for environment variables
- `api_key` is stored as `SecretStr` for security (use `get_api_key()` method to retrieve)

### 3.2 WatcherConfig Fields

| Field | Type | Default | Constraints | Description |
|-------|------|---------|-------------|-------------|
| `input_folder` | `Path` | `Path("./transcripts")` | Valid path | Directory to watch for transcript files |
| `output_folder` | `Path` | `Path("./outputs")` | Valid path | Directory where processed files are saved |
| `file_extensions` | `list[str]` | `[".txt", ".md"]` | List of strings | File extensions to watch (as list) |
| `poll_interval_seconds` | `float` | `5.0` | >= 1.0 | How often to check for new files (seconds) |
| `stability_check_seconds` | `float` | `2.0` | >= 0.5 | Time to wait for file stability (seconds) |
| `max_concurrent_files` | `int` | `3` | >= 1, <= 10 | Maximum number of files to process concurrently |
| `filename_template` | `str` | `{source_stem}_{timestamp}.md` | Valid template | Template for output filenames |

**Differences from Settings:**
- `file_extensions` is a `list[str]` (Settings uses comma-separated string)
- Does not include `state_file`, `model_provider`, `model_name`, or `api_key`
- Used internally by `TranscriptWatcher`

### 3.3 Configuration Precedence

Configuration values are resolved in the following order (highest to lowest priority):

1. **CLI Options** - Passed directly to commands (e.g., `--input-folder`, `--max-concurrent`)
2. **Environment Variables** - Prefixed with `MEETINGMIND_` (e.g., `MEETINGMIND_INPUT_FOLDER`)
3. **`.env` File** - Key-value pairs in `.env` file in current directory
4. **Default Values** - Hardcoded defaults in `Settings` and `WatcherConfig` classes

**Example Resolution:**

```bash
# .env file
MEETINGMIND_INPUT_FOLDER=/data/transcripts
MEETINGMIND_MAX_CONCURRENT_FILES=5

# Environment variable (overrides .env)
export MEETINGMIND_MAX_CONCURRENT_FILES=2

# CLI (overrides everything)
meetingmind watch --max-concurrent 4
# Result: max_concurrent_files = 4
```

### 3.4 get_watcher_config()

The `Settings.get_watcher_config()` method converts the application `Settings` into a `WatcherConfig` suitable for the `TranscriptWatcher`.

**Conversion Logic:**

1. **Split `file_extensions`**: The comma-separated string is split on commas
   ```python
   extensions = [ext.strip() for ext in self.file_extensions.split(",") if ext.strip()]
   ```

2. **Empty Extension Guard**: Raises `ValueError` if no valid extensions after splitting
   ```python
   if not extensions:
       raise ValueError("At least one file extension must be specified in MEETINGMIND_FILE_EXTENSIONS")
   ```

3. **Field Mapping**: Maps Settings fields to WatcherConfig fields
   - `input_folder` → `input_folder`
   - `output_folder` → `output_folder`
   - `file_extensions` (split list) → `file_extensions`
   - `poll_interval_seconds` → `poll_interval_seconds`
   - `stability_check_seconds` → `stability_check_seconds`
   - `max_concurrent_files` → `max_concurrent_files`
   - `filename_template` → `filename_template`

**Usage Example:**

```python
from meetingmind.config import load_settings

settings = load_settings()
watcher_config = settings.get_watcher_config()
# watcher_config.file_extensions is now [".txt", ".md"]
```

## 4. Data Models Reference

### Analysis Output Models

#### Summary

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `content` | `str` | Required | Concise meeting summary |
| `key_topics` | `list[str]` | `[]` | Main topics discussed |

**Purpose:** High-level overview extracted by `summary_agent`.

#### ActionPoint

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `description` | `str` | Required | What needs to be done |
| `owner` | `str \| None` | `None` | Person responsible |
| `deadline` | `str \| None` | `None` | Due date if mentioned |
| `priority` | `Literal["high", "medium", "low"]` | `"medium"` | Priority level |

**Purpose:** Single action item with assignee and priority.

#### ActionPoints

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `items` | `list[ActionPoint]` | `[]` | List of action items |

**Purpose:** Collection of action points extracted by `action_points_agent`.

#### TodoItem

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `task` | `str` | Required | Task description |
| `context` | `str \| None` | `None` | Additional context |

**Purpose:** Single todo item with optional context.

#### TodoList

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `items` | `list[TodoItem]` | `[]` | List of todo items |

**Purpose:** Collection of todos extracted by `todo_list_agent`.

#### ImportantMention

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `person` | `str` | Required | Person mentioned |
| `context` | `str` | Required | Context of the mention |
| `significance` | `str` | Required | Why this mention is important |

**Purpose:** Notable person/entity mention with context and significance.

#### ImportantMentions

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `items` | `list[ImportantMention]` | `[]` | List of important mentions |

**Purpose:** Collection of important mentions extracted by `important_mentions_agent`.

#### Recap

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `highlights` | `list[str]` | `[]` | Key highlights from the meeting |
| `decisions_made` | `list[str]` | `[]` | Decisions that were made |
| `next_steps` | `list[str]` | `[]` | Next steps to take |

**Purpose:** Meeting recap with highlights, decisions, and next steps extracted by `recap_agent`.

#### MeetingTone

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `overall_sentiment` | `Literal["positive", "neutral", "negative", "mixed"]` | `"neutral"` | Overall sentiment of the meeting |
| `energy_level` | `Literal["high", "medium", "low"]` | `"medium"` | Energy level during meeting |
| `collaboration_quality` | `Literal["excellent", "good", "fair", "poor"]` | `"good"` | Quality of collaboration |
| `notes` | `str \| None` | `None` | Additional observations about tone |

**Purpose:** Tone and dynamics analysis extracted by `meeting_tone_agent`.

#### KeyInsights

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `insights` | `list[str]` | `[]` | Important insights |
| `patterns` | `list[str]` | `[]` | Patterns observed |
| `recommendations` | `list[str]` | `[]` | Recommendations based on the meeting |

**Purpose:** Strategic insights and recommendations extracted by `key_insights_agent`.

#### TranscriptAnalysis

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `source_file` | `str` | Required | Original transcript filename |
| `processed_at` | `datetime` | Required | When analysis was completed (UTC) |
| `summary` | `Summary` | Required | Meeting summary |
| `action_points` | `ActionPoints` | Required | Action items |
| `todo_list` | `TodoList` | Required | Todo items |
| `important_mentions` | `ImportantMentions` | Required | Important mentions |
| `recap` | `Recap` | Required | Meeting recap |
| `meeting_tone` | `MeetingTone` | Required | Tone analysis |
| `key_insights` | `KeyInsights` | Required | Strategic insights |

**Purpose:** Root aggregation model containing all analysis results from the manager agent.

### State Models

#### ProcessedFileRecord

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `path` | `str` | Required | Absolute path to the processed file |
| `processed_at` | `datetime` | Required | When the file was processed |
| `output_path` | `str \| None` | `None` | Path to the generated output file |

**Purpose:** Record of a single processed file for state tracking.

#### ProcessedFilesState

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `version` | `int` | `1` | State format version |
| `files` | `dict[str, ProcessedFileRecord]` | `{}` | Map of absolute file path to record |

**Purpose:** Root state structure persisted to JSON file.

## 5. Agent System

### 5.1 _LazyAgent Class

**Purpose:**  
`_LazyAgent` is a proxy wrapper around Pydantic AI `Agent` instances that defers initialization until first use. This solves two key problems:

1. **API Key Requirement**: Avoids requiring API keys during module import/configuration
2. **Testing**: Enables easy model override with test models via context manager

**Constructor Parameters:**

```python
def __init__(self, model: str, register_tools_callback=None, **agent_kwargs)
```

- `model` (str): Model identifier (e.g., `"openai:gpt-4"`)
- `register_tools_callback` (callable, optional): Function to register tools on the agent after initialization
- `**agent_kwargs`: Additional keyword arguments passed to the Agent constructor
  - `result_type`: Pydantic model class for structured output (mapped to `output_type`)
  - `system_prompt`: System prompt string for the agent

**Key Properties and Methods:**

- `result_type` (property): Returns the configured `result_type` from agent kwargs
- `_get_agent()`: Internal method that creates the underlying `Agent` on first call
- `override(model=None, **kwargs)`: Returns context manager for temporary configuration override
- `__getattr__(name)`: Delegates attribute access to underlying agent (triggers initialization)
- `__call__(*args, **kwargs)`: Makes the proxy callable like the underlying agent

**Usage Example:**

```python
# Define lazy agent (no initialization yet)
summary_agent = _LazyAgent(
    "openai:gpt-4",
    result_type=Summary,
    system_prompt="You are an expert at summarizing meetings."
)

# First use triggers initialization
result = await summary_agent.run(transcript)  # Agent created here

# Testing with override
with summary_agent.override(model=TestModel()) as agent:
    result = await agent.run(transcript)  # Uses TestModel instead
```

### 5.2 ManagerContext

**Definition:**

```python
class ManagerContext:
    """Context for the manager agent."""

    def __init__(self, transcript: str, source_file: str):
        self.transcript = transcript
        self.source_file = source_file
```

**Purpose:**  
Provides dependency injection for the manager agent and its tools. The context is passed as `deps` parameter when calling `manager_agent.run()` and is accessible in tool functions via `RunContext[ManagerContext]`.

**Fields:**
- `transcript` (str): Full transcript text to be analyzed
- `source_file` (str): Original filename for reference

**Usage:**

```python
context = ManagerContext(transcript=transcript_text, source_file="meeting_20240115.txt")
result = await manager_agent.run(prompt, deps=context)
```

Inside tools:

```python
@agent.tool
async def get_summary(ctx: RunContext[ManagerContext]) -> Summary:
    # Access context via ctx.deps
    transcript = ctx.deps.transcript
    filename = ctx.deps.source_file
    # ...
```

### 5.3 Agent Inventory Table

| Variable | Model String | Output Type | Tool Name | System Prompt Focus |
|----------|-------------|-------------|-----------|---------------------|
| `summary_agent` | `openai:gpt-4` | `Summary` | N/A (worker) | Extract concise summary and identify main topics; focus on key points and outcomes |
| `action_points_agent` | `openai:gpt-4` | `ActionPoints` | N/A (worker) | Identify action items with specific tasks, assignments, deadlines, owners, and priority levels |
| `todo_list_agent` | `openai:gpt-4` | `TodoList` | N/A (worker) | Extract todo items that need completion with relevant context |
| `important_mentions_agent` | `openai:gpt-4` | `ImportantMentions` | N/A (worker) | Identify mentions of people, products, clients, or entities that are significant; explain importance |
| `recap_agent` | `openai:gpt-4` | `Recap` | N/A (worker) | Create meeting recap with key highlights, decisions made, and next steps; be specific and actionable |
| `meeting_tone_agent` | `openai:gpt-4` | `MeetingTone` | N/A (worker) | Analyze meeting tone and dynamics; assess sentiment, energy level, and collaboration quality objectively |
| `key_insights_agent` | `openai:gpt-4` | `KeyInsights` | N/A (worker) | Extract strategic insights; identify patterns and provide recommendations; think beyond the obvious |
| `manager_agent` | `openai:gpt-4` | `TranscriptAnalysis` | 7 tools registered | Orchestrate analysis; delegate work to specialized worker agents; aggregate results comprehensively |

**Manager Agent Tools (registered via `_register_manager_tools()`):**

1. `get_summary` - Calls `summary_agent`
2. `get_action_points` - Calls `action_points_agent`
3. `get_todo_list` - Calls `todo_list_agent`
4. `get_important_mentions` - Calls `important_mentions_agent`
5. `get_recap` - Calls `recap_agent`
6. `get_meeting_tone` - Calls `meeting_tone_agent`
7. `get_key_insights` - Calls `key_insights_agent`

### 5.4 analyze_transcript()

**Signature:**

```python
async def analyze_transcript(transcript: str, source_file: str) -> TranscriptAnalysis
```

**Parameters:**
- `transcript` (str): The full transcript text to analyze
- `source_file` (str): The original filename (for reference and metadata)

**Returns:**
- `TranscriptAnalysis`: Complete structured analysis with all fields populated

**Step-by-Step Description:**

1. **Create Context**: Instantiate `ManagerContext` with transcript and source_file
   ```python
   context = ManagerContext(transcript=transcript, source_file=source_file)
   ```

2. **Build Prompt**: Construct instruction for manager agent to use all worker tools
   ```python
   prompt = (
       f"Analyze the meeting transcript from '{source_file}'. "
       "Use the available tools to gather insights from specialized worker agents. "
       "Call all worker tools to get: summary, action points, todo list, "
       "important mentions, recap, meeting tone, and key insights. "
       "Then aggregate all results into a comprehensive TranscriptAnalysis."
   )
   ```

3. **Run Manager Agent**: Execute manager agent with prompt and context dependencies
   ```python
   result = await manager_agent.run(prompt, deps=context)
   ```
   - Manager agent determines which tools to call based on prompt
   - LLM orchestrates parallel tool execution
   - Each tool calls corresponding worker agent
   - Results are aggregated into `TranscriptAnalysis`

4. **Set Metadata**: Ensure source_file and processed_at are correctly set
   ```python
   analysis = result.output
   analysis.source_file = source_file
   analysis.processed_at = datetime.now(timezone.utc)
   ```

5. **Return Analysis**: Return the complete `TranscriptAnalysis` object

**Error Handling:**  
Exceptions from worker agents or the manager agent propagate up to the caller (`TranscriptWatcher._process_file()`).

### 5.5 Tool Registration Pattern

Tools are registered on the manager agent through the `_register_manager_tools()` callback, which is invoked when the `_LazyAgent` first initializes the underlying `Agent`.

**Registration Flow:**

1. **Define Callback**: Create function that accepts an `Agent` and registers tools on it
   ```python
   def _register_manager_tools(agent: Agent) -> None:
       @agent.tool
       async def get_summary(ctx: RunContext[ManagerContext]) -> Summary:
           result = await summary_agent.run(ctx.deps.transcript)
           return result.output
       # ... register other tools
   ```

2. **Pass to LazyAgent**: Provide callback when creating the manager agent
   ```python
   manager_agent = _LazyAgent(
       "openai:gpt-4",
       result_type=TranscriptAnalysis,
       system_prompt="...",
       register_tools_callback=_register_manager_tools,  # Callback here
   )
   ```

3. **Lazy Initialization**: On first agent access, `_LazyAgent._get_agent()`:
   - Creates the underlying `Agent`
   - Calls `register_tools_callback(agent)` if provided
   - Sets `_tools_registered = True` flag

4. **Tool Execution**: When the LLM calls a tool (e.g., `get_summary`):
   - Tool function receives `RunContext[ManagerContext]`
   - Accesses transcript via `ctx.deps.transcript`
   - Calls worker agent's `.run()` method
   - Returns structured Pydantic model (e.g., `Summary`)

**Pattern Benefits:**
- **Lazy Loading**: Tools only registered when agent is actually used
- **Dependency Injection**: Tools access context via `RunContext`
- **Type Safety**: Tool return types enforced by type hints
- **Separation**: Worker agents remain independent; tools act as proxies

**Complete Tool Example:**

```python
@agent.tool
async def get_action_points(ctx: RunContext[ManagerContext]) -> ActionPoints:
    """Get action points from action points worker agent."""
    # Access transcript from context
    transcript = ctx.deps.transcript
    
    # Call worker agent
    result = await action_points_agent.run(transcript)
    
    # Return structured output
    return result.output
```

## 6. State Management

### 6.1 StateStore Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `__init__(self, state_file: Path)` | Initialize StateStore with path to JSON state file |
| `load` | `load(self) -> ProcessedFilesState` | Load state from disk; returns cached state or creates new if file doesn't exist or is corrupted |
| `save` | `save(self) -> None` | Save current state to disk using atomic write (temp file + rename) |
| `is_processed` | `is_processed(self, file_path: Path) -> bool` | Check if a file (by absolute path) has already been processed |
| `mark_processed` | `mark_processed(self, file_path: Path, output_path: Path \| None = None) -> ProcessedFileRecord` | Mark a file as processed; creates record with current timestamp; saves state immediately |
| `get_record` | `get_record(self, file_path: Path) -> ProcessedFileRecord \| None` | Get the processing record for a specific file; returns None if not found |
| `get_all_processed` | `get_all_processed(self) -> list[ProcessedFileRecord]` | Get all processed file records as a list |
| `clear` | `clear(self) -> None` | Clear all state and delete the state file (used by `reset` command and testing) |

**Internal Behavior:**
- State is loaded once and cached in `_state` attribute
- All lookups use absolute paths via `file_path.resolve()`
- State file uses JSON format with Pydantic model serialization
- Corruption during load triggers warning and fresh state creation

### 6.2 State File JSON Schema

```json
{
  "version": 1,
  "files": {
    "/absolute/path/to/transcript1.txt": {
      "path": "/absolute/path/to/transcript1.txt",
      "processed_at": "2024-01-15T10:30:00.123456+00:00",
      "output_path": "/absolute/path/to/outputs/transcript1_20240115_103000.md"
    },
    "/absolute/path/to/transcript2.md": {
      "path": "/absolute/path/to/transcript2.md",
      "processed_at": "2024-01-15T11:45:30.987654+00:00",
      "output_path": "/absolute/path/to/outputs/transcript2_20240115_114530.md"
    }
  }
}
```

**Schema Details:**

- **Root Object**:
  - `version` (integer): State format version (currently always `1`)
  - `files` (object): Dictionary mapping absolute file paths to records

- **ProcessedFileRecord Object** (value in `files` dictionary):
  - `path` (string): Absolute path to the processed transcript file
  - `processed_at` (string): ISO 8601 datetime with timezone (UTC)
  - `output_path` (string | null): Absolute path to generated markdown file, or `null` if not recorded

**Notes:**
- All paths are absolute (resolved via `Path.resolve()`)
- Datetimes are serialized in ISO 8601 format with microsecond precision
- The key in the `files` dictionary matches the `path` field value (redundant but enables fast lookup)

### 6.3 Atomic Write Pattern

The `StateStore.save()` method uses an **atomic write pattern** to prevent state corruption:

**Implementation:**

```python
def save(self) -> None:
    """Save state to disk."""
    if self._state is None:
        return
    
    # Ensure parent directory exists
    self.state_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write atomically: write to temp file, then rename
    temp_file = self.state_file.with_suffix(".tmp")
    try:
        with open(temp_file, "w") as f:
            json.dump(self._state.model_dump(mode="json"), f, indent=2, default=str)
        temp_file.replace(self.state_file)
    except Exception as save_error:
        try:
            if temp_file.exists():
                temp_file.unlink()
        except Exception:
            pass  # Ignore cleanup errors to preserve original exception
        raise save_error
```

**Steps:**

1. **Check State**: Return early if no state to save
2. **Create Parent Directory**: Ensure directory exists for state file
3. **Write to Temp File**: Write JSON to `<statefile>.tmp`
   - Uses `model_dump(mode="json")` for Pydantic serialization
   - `default=str` handles datetime serialization
   - Pretty-printed with `indent=2`
4. **Atomic Rename**: Use `temp_file.replace(self.state_file)` to atomically replace the old file
   - On POSIX systems, `replace()` is atomic
   - If power loss occurs during write, either old file or new file exists (never partial/corrupted)
5. **Cleanup on Error**: If any exception occurs, attempt to delete temp file
   - Cleanup errors are suppressed to preserve the original exception
   - Original exception is re-raised

**Benefits:**
- **No Corruption**: File is never in a partially-written state
- **Crash Safety**: System crash during write leaves either old or new state, both valid
- **Concurrent Access**: Other processes never see incomplete data

### 6.4 Corruption Recovery

If the state file is corrupted (invalid JSON or invalid Pydantic model), the `StateStore` recovers gracefully:

**Detection:**

```python
try:
    with open(self.state_file, "r") as f:
        data = json.load(f)
    self._state = ProcessedFilesState.model_validate(data)
except (json.JSONDecodeError, ValueError) as e:
    # Corrupted state file, start fresh
    print(f"Warning: corrupted state file ({e}), starting fresh")
    self._state = ProcessedFilesState()
```

**Recovery Behavior:**

1. **Warning Printed**: User is notified of corruption with error details
2. **Fresh State Created**: New empty `ProcessedFilesState` instance is created
3. **Old Data Discarded**: Corrupted file is not deleted but is ignored
4. **Processing Continues**: All files will be considered unprocessed and reprocessed

**Impact:**
- **Data Loss**: Processing history is lost
- **Reprocessing**: Files that were previously processed will be processed again
- **No Crash**: Application continues running normally

**Prevention:**  
The atomic write pattern (Section 6.3) makes corruption extremely unlikely under normal circumstances. Corruption typically only occurs from:
- Manual file editing
- Filesystem errors
- External process writing to the file

## 7. File Processing Pipeline

The file processing pipeline consists of 9 sequential steps coordinated by `TranscriptWatcher`:

**1. File Discovery** (`_get_eligible_files()`)
   - **Module:** `watcher.py`
   - **Method:** `TranscriptWatcher._get_eligible_files()`
   - **Action:** Scan input folder for files matching configured extensions; filter out files already in state
   - **Error Behavior:** Returns empty list if input folder doesn't exist; continues

**2. File Stability Check** (`_is_file_stable()`)
   - **Module:** `watcher.py`
   - **Method:** `TranscriptWatcher._is_file_stable()`
   - **Action:** Record file size, wait `stability_check_seconds`, check if size unchanged
   - **Error Behavior:** Returns `False` on `OSError` (file deleted/inaccessible); file skipped for this cycle

**3. File Reading** (`_process_file()` - read step)
   - **Module:** `watcher.py`
   - **Method:** `TranscriptWatcher._process_file()` → `asyncio.to_thread(file_path.read_text)`
   - **Action:** Read entire file content as UTF-8 text
   - **Error Behavior:** Exception propagates; file NOT marked as processed; error printed; processing continues for other files

**4. Transcript Analysis** (`analyze_transcript()`)
   - **Module:** `agents.py`
   - **Method:** `analyze_transcript()`
   - **Action:** Create `ManagerContext`; run manager agent with prompt; manager calls 7 worker tools; aggregate results
   - **Error Behavior:** Exception propagates; file NOT marked as processed; error logged; Pydantic validation failures surface here

**5. Markdown Generation** (`generate_markdown()`)
   - **Module:** `markdown.py`
   - **Method:** `generate_markdown()`
   - **Action:** Convert `TranscriptAnalysis` to formatted markdown string with sections and emojis
   - **Error Behavior:** Should not fail (pure data transformation); any exception propagates; file NOT marked as processed

**6. Output Filename Generation** (`generate_output_filename()`)
   - **Module:** `markdown.py`
   - **Method:** `generate_output_filename()`
   - **Action:** Replace template placeholders (`{source_stem}`, `{timestamp}`) with actual values
   - **Error Behavior:** Should not fail; any exception propagates; file NOT marked as processed

**7. Output Directory Creation** (`mkdir`)
   - **Module:** `watcher.py`
   - **Method:** `TranscriptWatcher._process_file()` → `self.config.output_folder.mkdir()`
   - **Action:** Ensure output folder exists with `mkdir(parents=True, exist_ok=True)`
   - **Error Behavior:** `OSError` on permission denied propagates; file NOT marked as processed

**8. File Writing** (`write_text`)
   - **Module:** `watcher.py`
   - **Method:** `TranscriptWatcher._process_file()` → `asyncio.to_thread(output_path.write_text)`
   - **Action:** Write markdown content to output file as UTF-8
   - **Error Behavior:** Exception propagates; file NOT marked as processed; partial file may exist

**9. State Update** (`mark_processed()`)
   - **Module:** `state.py`
   - **Method:** `StateStore.mark_processed()`
   - **Action:** Create `ProcessedFileRecord` with current timestamp; add to state; save atomically
   - **Error Behavior:** Exception propagates but file has been successfully processed; state will be inconsistent (file may be reprocessed on restart)

**Concurrency Control:**
- Semaphore acquired at start of step 2 (stability check)
- Limits concurrent processing to `max_concurrent_files`
- Released automatically when `_process_file()` completes (success or error)

**Success Criteria:**
- File is only marked as processed (step 9) if all previous steps succeed
- On any error in steps 1-8, file remains unprocessed and will be retried

## 8. Concurrency Model

MeetingMind uses Python's `asyncio` for asynchronous I/O and bounded parallelism for safe concurrent processing.

### Semaphore Pattern

**Purpose:**  
Limit the number of files processed simultaneously to prevent resource exhaustion (API rate limits, memory usage).

**Implementation:**

```python
class TranscriptWatcher:
    def __init__(self, config: WatcherConfig, state_store: StateStore):
        # ...
        self._semaphore: asyncio.Semaphore | None = None
    
    async def watch(self) -> None:
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_files)
        # ...
    
    async def _process_file(self, file_path: Path) -> None:
        async with self._semaphore:
            # All processing happens within semaphore context
            # ...
```

**Behavior:**
- Semaphore is created with `max_concurrent_files` count (default: 3)
- `async with self._semaphore:` acquires a permit; blocks if none available
- When `_process_file()` completes (or raises exception), permit is released
- Ensures at most N files are being processed concurrently

**Example:**
If `max_concurrent_files=3` and 10 files are found:
- Files 1-3 start processing immediately
- Files 4-10 wait for a permit
- When file 1 completes, file 4 starts
- And so on until all 10 are processed

### gather with return_exceptions

**Purpose:**  
Process multiple files in parallel while capturing errors without stopping other tasks.

**Implementation:**

```python
async def _process_batch(self, files: list[Path]) -> None:
    """Process a batch of files with bounded concurrency."""
    if not files:
        return
    
    print(f"Found {len(files)} new file(s) to process")
    
    tasks = [self._process_file(file_path) for file_path in files]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Report any errors
    errors = [(files[i], r) for i, r in enumerate(results) if isinstance(r, Exception)]
    if errors:
        print(f"Completed batch with {len(errors)} error(s):")
        for file_path, error in errors:
            print(f"  - {file_path.name}: {error}")
```

**Behavior:**
- `asyncio.gather(*tasks)` runs all tasks concurrently
- `return_exceptions=True` captures exceptions as results instead of propagating immediately
- Results list contains either `None` (success) or `Exception` objects
- Errors are reported but don't stop processing of other files

**Example:**
- File 1: Success → result[0] = None
- File 2: API error → result[1] = Exception("API rate limit")
- File 3: Success → result[2] = None
- All three are processed; error printed at the end

### Watch Loop Poll Cycle

**Purpose:**  
Continuously monitor for new files while supporting graceful shutdown.

**Implementation:**

```python
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
                self._shutdown_event.wait(), 
                timeout=self.config.poll_interval_seconds
            )
            # If we got here, shutdown was triggered
            break
        except asyncio.TimeoutError:
            # Normal timeout, continue loop
            pass
    
    except Exception as e:
        print(f"Error in watch loop: {e}")
        await asyncio.sleep(self.config.poll_interval_seconds)
```

**Behavior:**
- Loop runs while `self._running` is `True`
- `asyncio.wait_for()` waits for shutdown event with timeout
- **Timeout (normal)**: `asyncio.TimeoutError` raised → continue to next cycle
- **Shutdown**: Event is set → no timeout → break loop
- **Error**: Caught, printed, sleep before retry

**Shutdown Timing:**
- If shutdown occurs during processing, current batch completes before loop exits
- If shutdown occurs during wait, loop exits immediately

### Signal Handling

**Purpose:**  
Enable graceful shutdown on SIGTERM/SIGINT (Ctrl+C).

**Implementation:**

```python
def _setup_signal_handlers(self) -> None:
    """Setup graceful shutdown handlers."""
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, self._signal_handler)

def _signal_handler(self, signum: int, frame: Any) -> None:
    """Handle shutdown signals."""
    print(f"\nReceived signal {signum}, initiating graceful shutdown...")
    self._running = False
    try:
        loop = asyncio.get_running_loop()
        loop.call_soon_threadsafe(self._shutdown_event.set)
    except RuntimeError:
        pass  # No running loop
```

**Behavior:**
- Registers handlers for SIGTERM (graceful termination) and SIGINT (Ctrl+C)
- On signal: sets `_running = False` and triggers `_shutdown_event`
- `call_soon_threadsafe()` safely sets event from signal handler (different thread)
- Watch loop detects event and exits gracefully

**Graceful Shutdown Flow:**
1. User presses Ctrl+C
2. Signal handler sets `_running = False` and `_shutdown_event`
3. Current processing batch completes
4. Watch loop detects event in `asyncio.wait_for()`
5. Loop breaks
6. "Shutdown complete" printed
7. Program exits

## 9. Output Format Specification

### 9.1 Filename Template

**Template String:**  
`{source_stem}_{timestamp}.md` (default)

**Supported Variables:**

| Variable | Description | Example |
|----------|-------------|---------|
| `{source_stem}` | Original filename without extension | `meeting_notes` (from `meeting_notes.txt`) |
| `{timestamp}` | Current timestamp in YYYYMMDD_HHMMSS format | `20240115_143022` |

**Template Processing:**  
The `generate_output_filename()` function performs simple string replacement:

```python
replacements = {
    "source_stem": source_file.stem,
    "timestamp": timestamp.strftime("%Y%m%d_%H%M%S"),
}
result = template
for key, value in replacements.items():
    result = result.replace(f"{{{key}}}", value)
```

**Example Transformations:**

| Template | Source File | Timestamp | Result |
|----------|------------|-----------|--------|
| `{source_stem}_{timestamp}.md` | `weekly_standup.txt` | 2024-01-15 14:30:22 | `weekly_standup_20240115_143022.md` |
| `analysis_{source_stem}.md` | `interview.md` | 2024-01-15 14:30:22 | `analysis_interview.md` |
| `{timestamp}_{source_stem}.md` | `planning.txt` | 2024-01-15 14:30:22 | `20240115_143022_planning.md` |
| `output.md` | `any_file.txt` | 2024-01-15 14:30:22 | `output.md` |

**Notes:**
- Template can be customized via `MEETINGMIND_FILENAME_TEMPLATE` environment variable
- Unsupported variables are left as-is (e.g., `{foo}` remains `{foo}`)
- No validation is performed on template; invalid filenames will cause write errors

### 9.2 Markdown Document Structure

The generated markdown document follows a consistent structure with 7 main sections:

**Complete Example:**

```markdown
# Meeting Analysis: team_sync_20240115.txt

**Processed:** 2024-01-15 14:30:22

---

## 📋 Summary

The team discussed Q1 product roadmap priorities, focusing on the new analytics dashboard and mobile app improvements. Key decisions were made regarding resource allocation and timeline adjustments.

**Key Topics:**

- Q1 Product Roadmap
- Analytics Dashboard Requirements
- Mobile App Performance
- Resource Allocation
- Timeline Review

## ✅ Action Points

### 1. 🔴 Complete analytics dashboard mockups

- **Owner:** Sarah Chen
- **Deadline:** January 20, 2024
- **Priority:** High

### 2. 🟡 Review mobile app performance metrics

- **Owner:** Alex Kumar
- **Deadline:** January 18, 2024
- **Priority:** Medium

### 3. 🟢 Update project documentation

- **Owner:** Jordan Lee
- **Priority:** Low

## 📝 Todo List

- [ ] Schedule follow-up meeting with stakeholders
  - *Context: Need to present updated roadmap and get approval*
- [ ] Prepare budget proposal for additional resources
  - *Context: Two additional engineers required for Q1 goals*
- [ ] Set up weekly sync meetings for Q1

## 👥 Important Mentions

### Sarah Chen

- **Context:** Mentioned as lead for analytics dashboard project
- **Significance:** Key decision-maker for dashboard design and implementation timeline

### Client: Acme Corp

- **Context:** Requested additional reporting features in the dashboard
- **Significance:** Major client whose requirements may influence Q1 priorities

## 🔄 Recap

**Highlights:**

- Agreed on Q1 product roadmap with analytics dashboard as top priority
- Identified need for two additional engineers to meet timeline
- Mobile app performance improvements moved to Q2

**Decisions Made:**

- Analytics dashboard will launch by March 15, 2024
- Budget increase of 20% approved for Q1
- Weekly sync meetings scheduled for Fridays at 2 PM

**Next Steps:**

- Sarah to complete mockups by January 20
- Alex to present performance analysis at next meeting
- Jordan to update all project documentation by end of week

## 🎭 Meeting Tone

- **Overall Sentiment:** Positive
- **Energy Level:** High
- **Collaboration Quality:** Excellent

**Notes:** Team showed strong enthusiasm for the new roadmap. Constructive discussions around resource constraints led to creative solutions.

## 💡 Key Insights

**Insights:**

- Team is aligned on strategic priorities for Q1
- Analytics capabilities are critical for customer retention
- Resource constraints are manageable with proper planning

**Patterns:**

- Consistent focus on customer-driven features
- Proactive identification of potential blockers
- Strong collaboration across engineering and product teams

**Recommendations:**

- Consider hiring additional QA resources to support increased development pace
- Establish clear success metrics for dashboard launch
- Implement weekly stakeholder updates to maintain alignment

---

*Generated by MeetingMind*
```

**Section Details:**

1. **Header**: Title with source filename, processing timestamp
2. **📋 Summary**: Concise overview and key topics list
3. **✅ Action Points**: Numbered list with priority emojis, owner, deadline
4. **📝 Todo List**: Checkbox list with optional context
5. **👥 Important Mentions**: Person/entity mentions with context and significance
6. **🔄 Recap**: Highlights, decisions made, next steps
7. **🎭 Meeting Tone**: Sentiment, energy, collaboration quality, optional notes
8. **💡 Key Insights**: Insights, patterns, recommendations
9. **Footer**: Generated by attribution

### 9.3 Value Reference Tables

#### Priority Emojis (Action Points)

| Priority | Emoji | Color | Use Case |
|----------|-------|-------|----------|
| `high` | 🔴 | Red | Urgent items requiring immediate attention |
| `medium` | 🟡 | Yellow | Important items with moderate urgency |
| `low` | 🟢 | Green | Nice-to-have items with low urgency |
| (other) | ⚪ | White | Fallback for unrecognized priority values |

**Usage in Code:**

```python
priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
emoji = priority_emoji.get(action.priority, "⚪")
```

#### Sentiment Options (Meeting Tone)

| Value | Description | When to Use |
|-------|-------------|-------------|
| `positive` | Optimistic, constructive, enthusiastic | Productive meetings with good outcomes |
| `neutral` | Balanced, matter-of-fact | Standard business meetings |
| `negative` | Tense, critical, pessimistic | Difficult discussions or bad news |
| `mixed` | Combination of positive and negative | Meetings with both good and challenging topics |

**Literal Type:** `Literal["positive", "neutral", "negative", "mixed"]`  
**Default:** `"neutral"`

#### Energy Level Options (Meeting Tone)

| Value | Description | Indicators |
|-------|-------------|-----------|
| `high` | Energetic, engaged, dynamic | Active participation, quick responses, enthusiasm |
| `medium` | Steady, focused | Normal business pace, adequate engagement |
| `low` | Subdued, passive | Minimal participation, fatigue, disengagement |

**Literal Type:** `Literal["high", "medium", "low"]`  
**Default:** `"medium"`

#### Collaboration Quality Options (Meeting Tone)

| Value | Description | Indicators |
|-------|-------------|-----------|
| `excellent` | Highly collaborative, supportive | Active listening, building on ideas, respectful disagreement |
| `good` | Generally collaborative | Most participants engaged, some good interactions |
| `fair` | Minimal collaboration | Limited interaction, mostly individual contributions |
| `poor` | Non-collaborative or contentious | Talking over each other, dismissive, unproductive conflicts |

**Literal Type:** `Literal["excellent", "good", "fair", "poor"]`  
**Default:** `"good"`

## 10. CLI Reference

### Command: `watch`

**Description:**  
Watch a folder for new transcript files and process them continuously. Runs until interrupted (Ctrl+C) or terminated (SIGTERM).

**Usage:**

```bash
meetingmind watch [OPTIONS]
```

**Options:**

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--input-folder PATH` | Path | Folder to watch for transcript files | `./transcripts` (or `MEETINGMIND_INPUT_FOLDER`) |
| `--output-folder PATH` | Path | Folder to write analysis markdown files | `./outputs` (or `MEETINGMIND_OUTPUT_FOLDER`) |
| `--poll-interval FLOAT` | Float | Seconds between folder checks | `5.0` (or `MEETINGMIND_POLL_INTERVAL_SECONDS`) |
| `--max-concurrent INT` | Integer | Maximum files to process concurrently | `3` (or `MEETINGMIND_MAX_CONCURRENT_FILES`) |

**Behavior:**

1. Loads configuration from environment variables and `.env` file
2. Overrides with CLI options if provided
3. Creates input folder if it doesn't exist
4. Prints startup information (folders, extensions, settings)
5. Enters watch loop:
   - Scans input folder every `poll-interval` seconds
   - Processes new files up to `max-concurrent` at a time
   - Skips files that are still being written (stability check)
   - Marks successfully processed files to avoid reprocessing
6. Runs until Ctrl+C or SIGTERM
7. Completes current batch before exiting (graceful shutdown)

**Exit Codes:**

| Code | Condition |
|------|-----------|
| `0` | Normal termination (Ctrl+C or SIGTERM) |
| `1` | Configuration error (e.g., no API key, invalid settings) |

**Example:**

```bash
# Watch default folders
meetingmind watch

# Custom folders with faster polling
meetingmind watch --input-folder /data/transcripts --output-folder /data/reports --poll-interval 2
```

---

### Command: `process`

**Description:**  
Process all unprocessed transcript files in the input folder once and exit. Does not watch for new files.

**Usage:**

```bash
meetingmind process [OPTIONS]
```

**Options:**

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--input-folder PATH` | Path | Folder to scan for transcript files | `./transcripts` (or `MEETINGMIND_INPUT_FOLDER`) |
| `--output-folder PATH` | Path | Folder to write analysis markdown files | `./outputs` (or `MEETINGMIND_OUTPUT_FOLDER`) |
| `--max-concurrent INT` | Integer | Maximum files to process concurrently | `3` (or `MEETINGMIND_MAX_CONCURRENT_FILES`) |
| `--transcript PATH` | Path | **Process a single transcript file directly by path** | None (processes all files in input folder) |

**Behavior:**

1. Loads configuration from environment variables and `.env` file
2. Overrides with CLI options if provided
3. Creates input and output folders if they don't exist
4. **If `--transcript` provided:**
   - Validates file exists and has valid extension
   - Processes only that single file
   - Ignores input folder and state (does not mark as processed)
5. **If no `--transcript` provided:**
   - Scans input folder for unprocessed files
   - Processes all eligible files up to `max-concurrent` at a time
   - Marks successfully processed files
6. Prints summary of files processed
7. Exits immediately after processing completes

**Exit Codes:**

| Code | Condition |
|------|-----------|
| `0` | All files processed successfully (or no files to process) |
| `1` | Interrupted by user (Ctrl+C) or configuration error |

**Examples:**

```bash
# Process all unprocessed files in default folder
meetingmind process

# Process all files in custom folder
meetingmind process --input-folder /data/transcripts --output-folder /data/reports

# Process a single file directly (ignores state)
meetingmind process --transcript /path/to/meeting_notes.txt
```

**Note on `--transcript` Option:**  
When using `--transcript`, the file:
- Can be located anywhere (not restricted to input folder)
- Must have an extension in `file_extensions` configuration
- Will NOT be marked as processed in state (useful for reprocessing)
- Will be processed even if already in state (useful for testing)

---

### Command: `status`

**Description:**  
Show processing status and statistics. Displays total count and details of recently processed files.

**Usage:**

```bash
meetingmind status
```

**Options:**

None

**Behavior:**

1. Loads state from state file
2. If no files processed, prints message and exits
3. Prints total count of processed files
4. Lists up to 10 most recently processed files with:
   - Filename
   - Processing timestamp
   - Output filename (if recorded)
5. Files are sorted by processing time (most recent first)

**Exit Codes:**

| Code | Condition |
|------|-----------|
| `0` | Always (success) |

**Example Output:**

```
Total files processed: 15

Recent files:
  • team_standup_20240115.txt
    Processed: 2024-01-15 14:30:22
    Output: team_standup_20240115_143022.md
  • project_review.md
    Processed: 2024-01-15 10:15:33
    Output: project_review_20240115_101533.md
  • ...
```

**Use Cases:**
- Check if a specific file has been processed
- Verify system is working correctly
- Audit processing history
- Troubleshoot processing issues

---

### Command: `reset`

**Description:**  
Reset processing state (clear all history). All files will be considered unprocessed and will be reprocessed on next `watch` or `process` command.

**Usage:**

```bash
meetingmind reset
```

**Options:**

None (requires confirmation)

**Behavior:**

1. Prompts for confirmation: "This will clear all processing history. Continue?"
2. If user confirms (y/yes):
   - Clears all records from state
   - Deletes state file from disk
   - Prints success message
3. If user declines (n/no):
   - Aborts operation
   - No changes made

**Exit Codes:**

| Code | Condition |
|------|-----------|
| `0` | State reset successfully or operation aborted |
| `1` | Error during reset (e.g., permission denied) |

**Example:**

```bash
$ meetingmind reset
This will clear all processing history. Continue? [y/N]: y
Processing state has been reset
```

**Warning:**  
This operation is **destructive and irreversible**. All processing history is lost. Files that were previously processed will be reprocessed on the next run.

**Use Cases:**
- Force reprocessing of all files (e.g., after changing AI models)
- Reset after testing
- Recover from corrupted state file
- Clear history before archiving/moving files

## 11. Development Guide

### 11.1 Prerequisites & Setup

**Prerequisites:**

- **Python 3.11 or higher**: Check version with `python --version` or `python3 --version`
- **uv**: Fast Python package installer and environment manager ([install instructions](https://github.com/astral-sh/uv))
- **AI Provider API Key**: OpenAI or Anthropic API key for agent functionality

**Setup Steps:**

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd MeetingMind
   ```

2. **Install UV** (if not already installed):

   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Install Dependencies:**

   ```bash
   # Install all dependencies including dev dependencies
   uv sync
   
   # Alternatively, use make
   make install
   ```

4. **Configure API Key:**

   Create a `.env` file in the project root:

   ```bash
   # For OpenAI
   MEETINGMIND_API_KEY=sk-...
   MEETINGMIND_MODEL_PROVIDER=openai
   MEETINGMIND_MODEL_NAME=gpt-4
   
   # For Anthropic
   MEETINGMIND_API_KEY=sk-ant-...
   MEETINGMIND_MODEL_PROVIDER=anthropic
   MEETINGMIND_MODEL_NAME=claude-3-opus-20240229
   ```

5. **Verify Installation:**

   ```bash
   # Run tests
   make test
   
   # Check CLI
   uv run meetingmind --version
   ```

6. **Create Test Folders:**

   ```bash
   mkdir transcripts outputs
   ```

**Development Environment:**

- Recommended: VS Code with Python extension
- Enable Ruff for linting/formatting
- Configure pytest for test discovery
- Use type hints for all new code

### 11.2 Makefile Reference

| Target | Command | Description |
|--------|---------|-------------|
| `help` | `make help` | Display all available make commands |
| `install` | `make install` | Install all dependencies using `uv sync` |
| `test` | `make test` | Run all tests with pytest in verbose mode |
| `tests` | `make tests` | Alias for `test` target |
| `lint` | `make lint` | Run Ruff linter to check code quality |
| `format` | `make format` | Format code with Ruff and auto-fix linting issues |
| `run` | `make run` | Run the watcher (equivalent to `meetingmind watch`) |
| `clean` | `make clean` | Remove build artifacts, dist files, egg-info, `__pycache__`, and `.pyc` files |

**Common Workflows:**

```bash
# Daily development
make format    # Format code before committing
make lint      # Check for issues
make test      # Run tests

# First-time setup
make install   # Install dependencies

# Running the application
make run       # Start watching for transcripts

# Cleanup
make clean     # Remove build artifacts
```

**Direct Commands (without Make):**

```bash
# Install
uv sync

# Test
uv run pytest tests/ -v

# Lint
uv run ruff check .

# Format
uv run ruff format .
uv run ruff check --fix .

# Run
uv run meetingmind watch
```

### 11.3 Testing

**Test Framework:**  
Tests use **pytest** with **pytest-asyncio** for async test support.

**Test Environment Configuration:**

Tests are designed to run without requiring actual AI model API calls. This is controlled by the `ALLOW_MODEL_REQUESTS` environment variable:

```python
# In tests/conftest.py or test files
ALLOW_MODEL_REQUESTS = os.getenv("ALLOW_MODEL_REQUESTS", "false").lower() == "true"
```

**Default Behavior (ALLOW_MODEL_REQUESTS=False):**
- Tests use `TestModel` from `pydantic-ai` for predictable, fast results
- No API keys required
- No external network calls
- Tests run in milliseconds

**Optional API Testing (ALLOW_MODEL_REQUESTS=True):**
- Tests use real AI models (requires API key in environment)
- Useful for integration testing with actual models
- Slower and may incur API costs

**TestModel Override Pattern:**

```python
from pydantic_ai import TestModel
from meetingmind.agents import summary_agent

async def test_summary_extraction():
    # Create test model with predefined response
    test_model = TestModel()
    
    # Override agent to use test model
    with summary_agent.override(model=test_model):
        result = await summary_agent.run("Sample transcript")
        assert result.output.content  # Verify output structure
```

**Running Tests:**

```bash
# Run all tests (using TestModel)
make test

# Run with actual API models (requires API key)
ALLOW_MODEL_REQUESTS=true make test

# Run specific test file
uv run pytest tests/test_agents.py -v

# Run specific test function
uv run pytest tests/test_agents.py::test_summary_extraction -v

# Run with coverage
uv run pytest tests/ --cov=meetingmind --cov-report=html
```

**Test Organization:**

- `tests/test_config.py` - Configuration loading and validation
- `tests/test_models.py` - Pydantic model validation
- `tests/test_agents.py` - Agent functionality with TestModel
- `tests/test_state.py` - State persistence and atomic writes
- `tests/test_markdown.py` - Markdown generation and templating
- `tests/test_watcher.py` - File watching and processing orchestration

**Pytest Configuration (pyproject.toml):**

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### 11.4 Adding a New Worker Agent

To add a new type of analysis (e.g., "Meeting Risks"), follow these 6 steps:

**1. Define the Output Model** (in `models.py`)

```python
class RiskItem(BaseModel):
    """A single identified risk."""
    description: str = Field(..., description="Description of the risk")
    severity: Literal["critical", "high", "medium", "low"] = Field(default="medium")
    mitigation: str | None = Field(None, description="Suggested mitigation")

class MeetingRisks(BaseModel):
    """Risks identified in the meeting."""
    items: list[RiskItem] = Field(default_factory=list)
```

**2. Add Field to TranscriptAnalysis** (in `models.py`)

```python
class TranscriptAnalysis(BaseModel):
    """Complete analysis aggregated by manager agent."""
    source_file: str
    processed_at: datetime
    summary: Summary
    action_points: ActionPoints
    todo_list: TodoList
    important_mentions: ImportantMentions
    recap: Recap
    meeting_tone: MeetingTone
    key_insights: KeyInsights
    meeting_risks: MeetingRisks  # NEW FIELD
```

**3. Create Worker Agent** (in `agents.py`)

```python
meeting_risks_agent = _LazyAgent(
    "openai:gpt-4",
    result_type=MeetingRisks,
    system_prompt=(
        "You are an expert at identifying risks in meeting discussions. "
        "Identify potential risks, blockers, or concerns that could impact "
        "project success. Assess severity and suggest mitigations."
    ),
)
```

**4. Register Tool on Manager Agent** (in `agents.py`, inside `_register_manager_tools()`)

```python
@agent.tool
async def get_meeting_risks(ctx: RunContext[ManagerContext]) -> MeetingRisks:
    """Get meeting risks from risks worker agent."""
    result = await meeting_risks_agent.run(ctx.deps.transcript)
    return result.output
```

**5. Update Markdown Generator** (in `markdown.py`)

```python
# In generate_markdown() function, add new section:

# Meeting Risks section
lines.extend([
    "## ⚠️ Meeting Risks",
    "",
])

if analysis.meeting_risks.items:
    for risk in analysis.meeting_risks.items:
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }
        emoji = severity_emoji.get(risk.severity, "⚪")
        
        lines.append(f"### {emoji} {risk.description}")
        lines.append(f"- **Severity:** {risk.severity.capitalize()}")
        if risk.mitigation:
            lines.append(f"- **Mitigation:** {risk.mitigation}")
        lines.append("")
else:
    lines.extend(["*No risks identified.*", ""])
```

**6. Update Manager Agent Prompt** (in `agents.py`, in `analyze_transcript()`)

```python
prompt = (
    f"Analyze the meeting transcript from '{source_file}'. "
    "Use the available tools to gather insights from specialized worker agents. "
    "Call all worker tools to get: summary, action points, todo list, "
    "important mentions, recap, meeting tone, key insights, and meeting risks. "  # Added
    "Then aggregate all results into a comprehensive TranscriptAnalysis."
)
```

**7. Write Tests** (create `tests/test_meeting_risks.py`)

```python
import pytest
from pydantic_ai import TestModel
from meetingmind.agents import meeting_risks_agent
from meetingmind.models import MeetingRisks, RiskItem

async def test_meeting_risks_extraction():
    """Test risk extraction with TestModel."""
    test_model = TestModel()
    
    with meeting_risks_agent.override(model=test_model):
        result = await meeting_risks_agent.run("Sample transcript")
        assert isinstance(result.output, MeetingRisks)
        assert isinstance(result.output.items, list)
```

**Complete!** The new worker agent is now integrated into the analysis pipeline.

### 11.5 Code Style

**Style Guide:**

MeetingMind follows PEP 8 with Ruff enforcement and project-specific configurations.

**Key Rules (from `pyproject.toml`):**

| Setting | Value | Rationale |
|---------|-------|-----------|
| **Line Length** | 100 characters | Balance readability and screen width |
| **Target Python** | 3.11+ | Use modern Python features |
| **Import Sorting** | isort-compatible | Consistent import order |
| **Linting Rules** | E, F, I, N, W, B, Q | Error, pyflakes, isort, naming, warnings, bugbear, quotes |
| **Ignored Rules** | E501 | Line length handled by formatter |

**Ruff Configuration:**

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "B", "Q"]
ignore = ["E501"]

[tool.ruff.lint.isort]
known-first-party = ["meetingmind"]
```

**Type Hints:**

All functions must have type hints for parameters and return values:

```python
# Good
async def analyze_transcript(transcript: str, source_file: str) -> TranscriptAnalysis:
    ...

# Bad
async def analyze_transcript(transcript, source_file):
    ...
```

**Async Patterns:**

- Use `async def` for all I/O-bound operations
- Use `asyncio.to_thread()` for blocking operations
- Always await async calls
- Use `async with` for context managers

**Docstrings:**

Use Google-style docstrings for public APIs:

```python
def generate_output_filename(template: str, source_file: Path, timestamp: datetime) -> str:
    """
    Generate output filename from template with placeholders.
    
    Supported placeholders:
    - {source_stem}: Original filename without extension
    - {timestamp}: Current timestamp in YYYYMMDD_HHMMSS format
    
    Args:
        template: Filename template string
        source_file: Source file path
        timestamp: Timestamp to use for generation
    
    Returns:
        Generated filename string
    """
```

**Code Organization:**

- One class per file (unless tightly coupled)
- Group related functions together
- Put helper functions after public functions
- Keep modules under 500 lines when possible

**Formatting Workflow:**

```bash
# Before committing
make format    # Auto-format and fix issues
make lint      # Check for remaining issues
```

**Pre-commit Hooks (Optional):**

Install pre-commit to enforce style automatically:

```bash
uv run pre-commit install
```

This runs Ruff on every commit to catch style issues early.

## 12. Error Reference

| Error Condition | Where Raised | Behavior | File Marked Processed | Recovery |
|----------------|--------------|----------|---------------------|----------|
| **Input folder doesn't exist** | `watcher.py:_get_eligible_files()` | Returns empty list; watch loop continues | N/A | Folder auto-created on next cycle; no manual intervention needed |
| **File not stable** | `watcher.py:_is_file_stable()` | Returns `False`; file skipped this cycle | No | File will be retried on next poll cycle when stable |
| **OSError during stability check** | `watcher.py:_is_file_stable()` | Returns `False`; file skipped | No | File deleted/moved/inaccessible; will not be retried unless recreated |
| **File read error (encoding, permission)** | `watcher.py:_process_file()` | Exception printed; file skipped | No | Check file encoding (must be UTF-8) and permissions; fix and will be retried |
| **Empty file extensions config** | `config.py:get_watcher_config()` | `ValueError` raised; program exits | N/A | Set `MEETINGMIND_FILE_EXTENSIONS` or use default; restart application |
| **Missing API key** | `agents.py` (on first agent call) | Exception from pydantic-ai; file skipped | No | Set `MEETINGMIND_API_KEY` environment variable; file will be retried |
| **API rate limit exceeded** | `agents.py` (during agent.run()) | API exception; file skipped | No | Wait for rate limit reset; file will be retried automatically |
| **Invalid API key** | `agents.py` (during agent.run()) | Authentication exception; file skipped | No | Correct `MEETINGMIND_API_KEY`; file will be retried |
| **Pydantic validation error (agent output)** | `agents.py` (after agent.run()) | ValidationError; file skipped | No | Usually model error; file may be retried but likely will fail again; check logs |
| **Output folder permission denied** | `watcher.py:_process_file()` | `OSError`; file skipped | No | Fix output folder permissions; file will be retried |
| **Disk full during write** | `watcher.py:_process_file()` | `OSError`; file skipped | No | Free disk space; file will be retried; partial output file may exist |
| **State file corrupted** | `state.py:load()` | Warning printed; fresh state created | N/A | All files considered unprocessed; will be reprocessed; old state discarded |
| **State file write error** | `state.py:save()` | Exception propagates; file WAS processed | **Yes (inconsistent state)** | File successfully processed but not recorded; will be reprocessed on restart; manual state edit possible |
| **CTRL+C during watch** | `main.py:watch()` | Graceful shutdown initiated; current batch completes | Depends on timing | Resume with `watch` command; incomplete files will be retried |
| **SIGTERM during watch** | `watcher.py:_signal_handler()` | Graceful shutdown initiated; current batch completes | Depends on timing | Resume with `watch` command; incomplete files will be retried |
| **Invalid file extension** | `watcher.py:process_single_file()` | `ValueError` raised; command exits | No | Use valid extension in config or rename file; rerun command |
| **File not found (process --transcript)** | `watcher.py:process_single_file()` | `FileNotFoundError` raised; command exits | No | Check file path; correct and rerun command |
| **Model provider error (network timeout)** | `agents.py` (during agent.run()) | Network exception; file skipped | No | Check network connection; file will be retried automatically |
| **LLM refuses to output structured data** | `agents.py` (during agent.run()) | Pydantic AI error; file skipped | No | Rare; may indicate transcript format issue or model problem; retry or check transcript content |

**General Error Handling Principles:**

1. **Errors During Processing**: File is NOT marked as processed and will be retried on next cycle
2. **Graceful Degradation**: Individual file errors don't stop processing of other files
3. **State Safety**: State is only updated after successful processing (except state write errors)
4. **Atomic Writes**: State file uses atomic write pattern to prevent corruption
5. **User Notification**: All errors are printed to console with context (filename, error message)
6. **Automatic Retry**: Failed files are automatically retried on next watch cycle or process run
7. **No Silent Failures**: All errors are reported; no files are silently skipped without notification

**Troubleshooting Tips:**

- **Check Logs**: All errors print to stdout/stderr with context
- **Verify Configuration**: Use `meetingmind status` to check state
- **Test Single File**: Use `meetingmind process --transcript <path>` to test one file
- **Reset State**: Use `meetingmind reset` if state is corrupted or needs clearing
- **Check API Key**: Verify `MEETINGMIND_API_KEY` is set correctly in `.env`
- **Monitor Disk Space**: Ensure sufficient space for output files
- **Review Permissions**: Check read access to input folder and write access to output folder

---

**Document Version:** 1.0  
**Last Updated:** 2024-01-15  
**MeetingMind Version:** 0.1.0

