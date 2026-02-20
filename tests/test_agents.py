"""Test agent orchestration using Pydantic AI testing tools."""

import pytest
from pydantic_ai import models
from pydantic_ai.models.test import TestModel

from meetingmind.agents import (
    action_points_agent,
    analyze_transcript,
    key_insights_agent,
    manager_agent,
    meeting_tone_agent,
    recap_agent,
    summary_agent,
    todo_list_agent,
)
from meetingmind.models import (
    ActionPoint,
    ActionPoints,
    KeyInsights,
    MeetingTone,
    Recap,
    Summary,
    TodoItem,
    TodoList,
)


@pytest.fixture
def sample_transcript():
    """Sample transcript for testing."""
    return """
    Meeting Transcript - Q4 Planning
    Date: 2024-01-15

    Alice: Welcome everyone. Today we need to discuss our Q4 goals.
    Bob: I think we should focus on improving our API performance.
    Alice: Good point. Let's make that an action item for you, Bob. Can you have a plan by next Friday?
    Bob: Absolutely. I'll get that done.
    Charlie: We also need to update our documentation.
    Alice: Charlie, can you own that? Let's aim for end of month.
    Charlie: Sure thing.
    Alice: Great meeting everyone. The team energy is really positive today.
    """


@pytest.mark.asyncio
async def test_summary_agent_with_test_model(sample_transcript, subtests):
    """Test summary agent using TestModel."""
    # Create a test model that returns a predefined summary
    test_summary = Summary(
        content="Team discussed Q4 planning and assigned action items",
        key_topics=["Q4 Goals", "API Performance", "Documentation"],
    )

    with summary_agent.override(model=TestModel(custom_output_text=test_summary.model_dump_json())):
        result = await summary_agent.run(sample_transcript)

        with subtests.test("returns_summary"):
            assert isinstance(result.data, Summary)

        with subtests.test("has_content"):
            assert len(result.data.content) > 0


@pytest.mark.asyncio
async def test_action_points_agent_with_test_model(sample_transcript, subtests):
    """Test action points agent using TestModel."""
    test_actions = ActionPoints(
        items=[
            ActionPoint(description="Create API performance plan", owner="Bob", priority="high"),
            ActionPoint(description="Update documentation", owner="Charlie", priority="medium"),
        ]
    )

    with action_points_agent.override(
        model=TestModel(custom_output_text=test_actions.model_dump_json())
    ):
        result = await action_points_agent.run(sample_transcript)

        with subtests.test("returns_action_points"):
            assert isinstance(result.data, ActionPoints)

        with subtests.test("has_items"):
            assert isinstance(result.data.items, list)


@pytest.mark.asyncio
async def test_todo_list_agent_with_test_model(sample_transcript, subtests):
    """Test todo list agent using TestModel."""
    test_todos = TodoList(
        items=[
            TodoItem(task="Prepare API performance analysis"),
            TodoItem(task="Review current documentation"),
        ]
    )

    with todo_list_agent.override(model=TestModel(custom_output_text=test_todos.model_dump_json())):
        result = await todo_list_agent.run(sample_transcript)

        with subtests.test("returns_todo_list"):
            assert isinstance(result.data, TodoList)

        with subtests.test("has_items"):
            assert isinstance(result.data.items, list)


@pytest.mark.asyncio
async def test_recap_agent_with_test_model(sample_transcript, subtests):
    """Test recap agent using TestModel."""
    test_recap = Recap(
        highlights=["Q4 planning initiated"],
        decisions_made=["Focus on API performance"],
        next_steps=["Bob to create plan by Friday"],
    )

    with recap_agent.override(model=TestModel(custom_output_text=test_recap.model_dump_json())):
        result = await recap_agent.run(sample_transcript)

        with subtests.test("returns_recap"):
            assert isinstance(result.data, Recap)

        with subtests.test("has_highlights"):
            assert isinstance(result.data.highlights, list)


@pytest.mark.asyncio
async def test_meeting_tone_agent_with_test_model(sample_transcript, subtests):
    """Test meeting tone agent using TestModel."""
    test_tone = MeetingTone(
        overall_sentiment="positive",
        energy_level="high",
        collaboration_quality="excellent",
        notes="Team showed strong engagement",
    )

    with meeting_tone_agent.override(
        model=TestModel(custom_output_text=test_tone.model_dump_json())
    ):
        result = await meeting_tone_agent.run(sample_transcript)

        with subtests.test("returns_tone"):
            assert isinstance(result.data, MeetingTone)

        with subtests.test("has_sentiment"):
            assert result.data.overall_sentiment in ["positive", "neutral", "negative", "mixed"]


@pytest.mark.asyncio
async def test_key_insights_agent_with_test_model(sample_transcript, subtests):
    """Test key insights agent using TestModel."""
    test_insights = KeyInsights(
        insights=["Team alignment on priorities"],
        patterns=["Clear ownership assignment"],
        recommendations=["Maintain current collaboration approach"],
    )

    with key_insights_agent.override(
        model=TestModel(custom_output_text=test_insights.model_dump_json())
    ):
        result = await key_insights_agent.run(sample_transcript)

        with subtests.test("returns_insights"):
            assert isinstance(result.data, KeyInsights)

        with subtests.test("has_insights"):
            assert isinstance(result.data.insights, list)


@pytest.mark.asyncio
async def test_agent_types(subtests):
    """Test that all agents have correct result types."""
    with subtests.test("summary_agent"):
        assert summary_agent.result_type == Summary

    with subtests.test("action_points_agent"):
        assert action_points_agent.result_type == ActionPoints

    with subtests.test("todo_list_agent"):
        assert todo_list_agent.result_type == TodoList

    with subtests.test("recap_agent"):
        assert recap_agent.result_type == Recap

    with subtests.test("meeting_tone_agent"):
        assert meeting_tone_agent.result_type == MeetingTone

    with subtests.test("key_insights_agent"):
        assert key_insights_agent.result_type == KeyInsights
