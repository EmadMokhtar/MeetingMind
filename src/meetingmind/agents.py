"""Pydantic AI agents for transcript analysis."""

import asyncio
from datetime import datetime, timezone
from typing import Any

from pydantic_ai import Agent, RunContext

from meetingmind.models import (
    ActionPoints,
    ImportantMentions,
    KeyInsights,
    MeetingTone,
    Recap,
    Summary,
    TodoList,
    TranscriptAnalysis,
)


class _LazyAgent:
    """Proxy that lazily initializes an Agent on first access."""

    def __init__(self, model: str, register_tools_callback=None, **agent_kwargs):
        self._model = model
        self._agent_kwargs = agent_kwargs
        self._agent = None
        self._register_tools_callback = register_tools_callback
        self._tools_registered = False

    @property
    def result_type(self):
        """Get the configured result type for this agent."""
        return self._agent_kwargs.get('result_type')

    def _get_agent(self) -> Agent:
        """Get or create the underlying agent."""
        if self._agent is None:
            # Map our simplified parameter names to pydantic-ai's Agent parameters
            agent_kwargs = {}
            if 'result_type' in self._agent_kwargs:
                agent_kwargs['output_type'] = self._agent_kwargs['result_type']
            if 'system_prompt' in self._agent_kwargs:
                agent_kwargs['system_prompt'] = self._agent_kwargs['system_prompt']
            
            self._agent = Agent(self._model, **agent_kwargs)
            # Register tools if callback provided
            if self._register_tools_callback and not self._tools_registered:
                self._register_tools_callback(self._agent)
                self._tools_registered = True
        return self._agent

    def override(self, model=None, **kwargs):
        """
        Override configuration without initializing the original agent.
        
        For testing, we can override with a TestModel directly without needing
        to initialize the original Agent that requires API keys.
        """
        if model is not None:
            # Create a new temporary agent with the override model
            # Use the same configuration as the original agent
            temp_kwargs = {}
            if 'result_type' in self._agent_kwargs:
                temp_kwargs['output_type'] = self._agent_kwargs['result_type']
            if 'system_prompt' in self._agent_kwargs:
                temp_kwargs['system_prompt'] = self._agent_kwargs['system_prompt']
            
            temp_agent = Agent(model, **temp_kwargs)
            # Register tools if needed
            if self._register_tools_callback:
                self._register_tools_callback(temp_agent)
            # Return context manager that temporarily replaces the agent
            return _OverrideContext(self, temp_agent)
        else:
            # No model override, so we need the real agent
            agent = self._get_agent()
            return agent.override(**kwargs)

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the underlying agent."""
        return getattr(self._get_agent(), name)

    def __call__(self, *args, **kwargs):
        """Make the proxy callable like the underlying agent."""
        return self._get_agent()(*args, **kwargs)


class _OverrideContext:
    """Context manager that temporarily replaces the agent in a LazyAgent."""
    
    def __init__(self, lazy_agent: '_LazyAgent', override_agent: Agent):
        self._lazy_agent = lazy_agent
        self._override_agent = override_agent
        self._original_agent = None
    
    def __enter__(self):
        # Save the original agent (which might be None)
        self._original_agent = self._lazy_agent._agent
        # Replace with the override agent
        self._lazy_agent._agent = self._override_agent
        self._lazy_agent._tools_registered = True  # Tools already registered on override agent
        return self._override_agent
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore the original agent
        self._lazy_agent._agent = self._original_agent
        if self._original_agent is None:
            self._lazy_agent._tools_registered = False
        return False


# Worker agents - each specialized in extracting specific information
summary_agent = _LazyAgent(
    "openai:gpt-4",
    result_type=Summary,
    system_prompt=(
        "You are an expert at summarizing meeting transcripts. "
        "Extract a concise summary and identify the main topics discussed. "
        "Focus on the key points and outcomes."
    ),
)

action_points_agent = _LazyAgent(
    "openai:gpt-4",
    result_type=ActionPoints,
    system_prompt=(
        "You are an expert at identifying action items from meeting transcripts. "
        "Extract specific tasks, assignments, and deadlines. "
        "Identify who is responsible and the priority level."
    ),
)

todo_list_agent = _LazyAgent(
    "openai:gpt-4",
    result_type=TodoList,
    system_prompt=(
        "You are an expert at extracting todo items from meeting transcripts. "
        "Identify tasks that need to be completed, with relevant context."
    ),
)

important_mentions_agent = _LazyAgent(
    "openai:gpt-4",
    result_type=ImportantMentions,
    system_prompt=(
        "You are an expert at identifying important mentions in meeting transcripts. "
        "Extract mentions of people, products, clients, or entities that are significant. "
        "Explain why each mention is important."
    ),
)

recap_agent = _LazyAgent(
    "openai:gpt-4",
    result_type=Recap,
    system_prompt=(
        "You are an expert at creating meeting recaps. "
        "Identify key highlights, decisions made, and next steps. "
        "Be specific and actionable."
    ),
)

meeting_tone_agent = _LazyAgent(
    "openai:gpt-4",
    result_type=MeetingTone,
    system_prompt=(
        "You are an expert at analyzing meeting tone and dynamics. "
        "Assess the overall sentiment, energy level, and collaboration quality. "
        "Provide objective observations based on the transcript."
    ),
)

key_insights_agent = _LazyAgent(
    "openai:gpt-4",
    result_type=KeyInsights,
    system_prompt=(
        "You are an expert at extracting strategic insights from meetings. "
        "Identify important insights, patterns, and provide recommendations. "
        "Think beyond the obvious and find deeper meaning."
    ),
)


# Manager agent context
class ManagerContext:
    """Context for the manager agent."""

    def __init__(self, transcript: str, source_file: str):
        self.transcript = transcript
        self.source_file = source_file


def _register_manager_tools(agent: Agent) -> None:
    """Register tools on the manager agent when it's first initialized."""

    @agent.tool
    async def get_summary(ctx: RunContext[ManagerContext]) -> Summary:
        """Get meeting summary from summary worker agent."""
        result = await summary_agent.run(ctx.deps.transcript)
        return result.output

    @agent.tool
    async def get_action_points(ctx: RunContext[ManagerContext]) -> ActionPoints:
        """Get action points from action points worker agent."""
        result = await action_points_agent.run(ctx.deps.transcript)
        return result.output

    @agent.tool
    async def get_todo_list(ctx: RunContext[ManagerContext]) -> TodoList:
        """Get todo list from todo list worker agent."""
        result = await todo_list_agent.run(ctx.deps.transcript)
        return result.output

    @agent.tool
    async def get_important_mentions(ctx: RunContext[ManagerContext]) -> ImportantMentions:
        """Get important mentions from important mentions worker agent."""
        result = await important_mentions_agent.run(ctx.deps.transcript)
        return result.output

    @agent.tool
    async def get_recap(ctx: RunContext[ManagerContext]) -> Recap:
        """Get meeting recap from recap worker agent."""
        result = await recap_agent.run(ctx.deps.transcript)
        return result.output

    @agent.tool
    async def get_meeting_tone(ctx: RunContext[ManagerContext]) -> MeetingTone:
        """Get meeting tone analysis from tone worker agent."""
        result = await meeting_tone_agent.run(ctx.deps.transcript)
        return result.output

    @agent.tool
    async def get_key_insights(ctx: RunContext[ManagerContext]) -> KeyInsights:
        """Get key insights from insights worker agent."""
        result = await key_insights_agent.run(ctx.deps.transcript)
        return result.output


# Manager agent - orchestrates workers and aggregates results
manager_agent = _LazyAgent(
    "openai:gpt-4",
    result_type=TranscriptAnalysis,
    system_prompt=(
        "You are a manager agent that orchestrates analysis of meeting transcripts. "
        "You delegate work to specialized worker agents and aggregate their results "
        "into a comprehensive analysis."
    ),
    register_tools_callback=_register_manager_tools,
)


async def analyze_transcript(transcript: str, source_file: str) -> TranscriptAnalysis:
    """
    Analyze a transcript using manager-worker orchestration.

    The manager agent coordinates multiple worker agents to extract
    different aspects of the transcript in parallel.
    """
    context = ManagerContext(transcript=transcript, source_file=source_file)

    prompt = (
        f"Analyze the meeting transcript from '{source_file}'. "
        "Use the available tools to gather insights from specialized worker agents. "
        "Call all worker tools to get: summary, action points, todo list, "
        "important mentions, recap, meeting tone, and key insights. "
        "Then aggregate all results into a comprehensive TranscriptAnalysis."
    )

    result = await manager_agent.run(prompt, deps=context)

    # Ensure the source_file and processed_at are set correctly
    analysis = result.output
    analysis.source_file = source_file
    analysis.processed_at = datetime.now(timezone.utc)

    return analysis
