# Pydantic AI - Copilot Workspace Instructions

This project uses **Pydantic AI** to build agentic workflows and AI-powered applications.
Always follow these conventions when generating or modifying Python code.

## Core Stack

- **Pydantic AI** - agent framework (`pydantic-ai`)
- **Pydantic v2** - data validation and structured outputs
- **Python 3.11+** - use modern typing (`list`, `dict`, `X | Y`) and `asyncio`
- **FastAPI** - web framework for APIs (referred to as "WebAPI" in instruction files)
- **uv** - package installer and virtual environment management
- **Ruff** - linter and formatter (line length: 120)
- **mypy** - static type checker
- **structlog** - structured logging
- **pytest** - testing framework (⛔ always run via `make test` or `uv run pytest` — NEVER `python -m pytest` or bare `pytest`)
- **Prometheus** - metrics (`prometheus-client`)
- **`python-dotenv`** - load API keys from `.env`

## Key Principles

1. **Typed everything** - `deps_type` and `output_type` must be Pydantic models or dataclasses. Never use raw `dict` or `Any` for structured data.
2. **Async-first** - prefer `async def` for tools and agent runs; use `run_sync` only in scripts or tests.
3. **Dependency injection** - pass services, clients, and config through `deps_type`; never use global state inside tools.
4. **Structured outputs** - define `output_type` with a Pydantic model whenever the agent should return structured data.
5. **Explicit model strings** - always include the provider prefix: `"openai:gpt-4o"`, `"anthropic:claude-3-5-sonnet-latest"`, etc.
6. **Agents are global** - instantiate agents at module level and reuse them, like FastAPI routers.

## Critical API Reference

| Concept | Correct usage |
|---|---|
| Structured output param | `output_type=MyModel` |
| Result access | `result.output` |
| Static instructions kwarg | `instructions=` or `system_prompt=` (both valid) |
| Dynamic instructions decorator | `@agent.system_prompt` or `@agent.instructions` |
| OpenAI model class | `OpenAIChatModel` (not `OpenAIModel`) |
| Continue conversation | `message_history=result.new_messages()` |
| Usage rollup to parent | `usage=ctx.usage` in sub-agent call |
| Output validation | `@agent.output_validator` |
| External tool collections | `toolsets=[server]` |

## Project Layout Convention

```
src/
  agents/          # one file per agent or agent group
  tools/           # reusable tool functions
  models/          # Pydantic models for deps and outputs
  workflows/       # multi-agent orchestration logic
  routers/         # FastAPI routers
  services/        # business logic / service layer
  dependencies.py  # FastAPI dependency injection
  main.py
tests/
  unit/
  integration/
.github/
  agents/          # custom Copilot agents (*.agent.md)
  instructions/    # scoped instruction files (*.instructions.md)
  prompts/         # reusable prompt files (*.prompt.md)
  skills/          # module skill files (<module>.skill.md)
.env               # API keys (never committed)
pyproject.toml     # Ruff, mypy, pytest config
Makefile           # make test, make lint, make run
```

## Instruction Files

| Topic | File |
|---|---|
| Agent creation, instructions, output types, running, streaming | `.github/instructions/pydantic-ai-agents.instructions.md` |
| Tools, tool_plain, toolsets, output validators | `.github/instructions/pydantic-ai-tools.instructions.md` |
| Multi-agent workflows, delegation, hand-off, sessions | `.github/instructions/pydantic-ai-workflows.instructions.md` |
| Model providers, settings, fallback, concurrency | `.github/instructions/pydantic-ai-models.instructions.md` |
| Multimodal input: images, audio, video, documents | `.github/instructions/pydantic-ai-input.instructions.md` |
| MCP (Model Context Protocol) integration | `.github/instructions/pydantic-ai-mcp.instructions.md` |
| Embeddings and vector search / RAG | `.github/instructions/pydantic-ai-embeddings.instructions.md` |
| Unit testing (TestModel, FunctionModel, fixtures) | `.github/instructions/pydantic-ai-testing.instructions.md` |
| Python standards, Ruff rules, imports, logging | `.github/instructions/python.instructions.md` |
| FastAPI endpoints, schemas, dependency injection | `.github/instructions/api.instructions.md` |
| Pytest standards, subtests, fixtures, make test | `.github/instructions/pytest.instructions.md` |
| Conventional commits, scopes, breaking changes | `.github/instructions/commit.instructions.md` |
| Docker multi-stage builds, uv, Artifactory | `.github/instructions/docker.instructions.md` |
| Module skills (capabilities, APIs, usage) | `.github/instructions/skills.instructions.md` |

## Custom Agents

Invoke specialized agents in Copilot Chat with `@agent-name`:

| Agent | Role | When to Use |
|---|---|---|
| `@orchestrator` | Design + delegate to all other agents | Complex features from start to finish |
| `@lead-software-engineer` | Hands-on complex/critical implementation | Architecture, security-sensitive code |
| `@senior-software-engineer-implementation` | Standard feature implementation | Create, build, add features |
| `@senior-software-engineer-reviewer` | Code review (score 0-100%) | Review PRs, quality gates (target: 90%+) |
| `@senior-qa-engineer` | Test automation and QA | Write tests, improve coverage |
| `@senior-security-engineer` | Security review (read-only) | OWASP checks, auth review |
| `@senior-devops-engineer` | CI/CD, Docker, infrastructure | Pipelines, containers, cloud |
| `@technical-writer` | Documentation | README, API docs, guides |

See `.github/agents/README.agent.md` for full details, tool access matrix, and workflow guides.

## Reusable Prompts

Pre-built prompts in `.github/prompts/` for common tasks:

| Prompt | Purpose |
|---|---|
| `feature-implementation.prompt.md` | Implement a new feature following project standards |
| `fix-bug.prompt.md` | Debug and fix issues systematically |
| `refactor-code.prompt.md` | Improve code quality without changing behavior |
| `create-api-endpoint.prompt.md` | Add a FastAPI endpoint with full stack |
| `code-review.prompt.md` | Thorough code review checklist |
| `write-tests.prompt.md` | Generate comprehensive test suites |
| `security-audit.prompt.md` | OWASP-based security review |
| `docker-setup.prompt.md` | Create/modify Docker configurations |
| `add-monitoring.prompt.md` | Add observability and metrics |
| `write-documentation.prompt.md` | Create feature documentation |
| `create-pr-description.prompt.md` | Generate concise PR descriptions |
| `model-recommendation.prompt.md` | Recommend optimal AI models for a task |
| `ai-prompt-engineering-safety-review.prompt.md` | Review AI prompts for safety and quality |

See `.github/prompts/README.md` for usage examples and workflows.

## Module Skills

Every source module has a companion skill file in `.github/skills/`:

| Module | Skill File |
|--------|-----------|
| `agents.py` | `.github/skills/agents.skill.md` |
| `config.py` | `.github/skills/config.skill.md` |
| `main.py` | `.github/skills/main.skill.md` |
| `markdown.py` | `.github/skills/markdown.skill.md` |
| `models.py` | `.github/skills/models.skill.md` |
| `state.py` | `.github/skills/state.skill.md` |
| `watcher.py` | `.github/skills/watcher.skill.md` |

### Rules for all agents

- **Before modifying a module** — read its skill file to understand the current API and design decisions
- **After modifying a module** — flag that the skill file needs updating (engineers flag; technical writer updates)
- **New modules** — create a skill file before or immediately after the module is merged
- **Skill file format** — follow `.github/instructions/skills.instructions.md`

## Core Imports

```python
from pydantic_ai import Agent, RunContext, ModelRetry, UsageLimits
from pydantic_ai import ModelMessagesTypeAdapter
from pydantic_ai import ImageUrl, BinaryContent, DocumentUrl, AudioUrl, VideoUrl
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.mcp import MCPServerStreamableHTTP, MCPServerStdio
from pydantic_ai import Embedder
from pydantic import BaseModel, Field
```

## Environment Variables

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
GROQ_API_KEY=gsk_...
```

Load before creating any agent:
```python
from dotenv import load_dotenv
load_dotenv()
```
