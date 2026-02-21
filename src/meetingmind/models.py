"""Pydantic models for structured agent outputs."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Summary(BaseModel):
    """Meeting summary extracted by worker agent."""

    content: str = Field(..., description="Concise meeting summary")
    key_topics: list[str] = Field(default_factory=list, description="Main topics discussed")


class ActionPoint(BaseModel):
    """Single action item extracted from transcript."""

    description: str = Field(..., description="What needs to be done")
    owner: str | None = Field(None, description="Person responsible")
    deadline: str | None = Field(None, description="Due date if mentioned")
    priority: Literal["high", "medium", "low"] = Field(default="medium")


class ActionPoints(BaseModel):
    """Action points extracted by worker agent."""

    items: list[ActionPoint] = Field(default_factory=list)


class TodoItem(BaseModel):
    """Single todo item extracted from transcript."""

    task: str = Field(..., description="Task description")
    context: str | None = Field(None, description="Additional context")


class TodoList(BaseModel):
    """Todo list extracted by worker agent."""

    items: list[TodoItem] = Field(default_factory=list)


class ImportantMention(BaseModel):
    """Important mention from the meeting."""

    person: str = Field(..., description="Person mentioned")
    context: str = Field(..., description="Context of the mention")
    significance: str = Field(..., description="Why this mention is important")


class ImportantMentions(BaseModel):
    """Important mentions extracted by worker agent."""

    items: list[ImportantMention] = Field(default_factory=list)


class Recap(BaseModel):
    """Meeting recap extracted by worker agent."""

    highlights: list[str] = Field(
        default_factory=list, description="Key highlights from the meeting"
    )
    decisions_made: list[str] = Field(default_factory=list, description="Decisions that were made")
    next_steps: list[str] = Field(default_factory=list, description="Next steps to take")


class MeetingTone(BaseModel):
    """Meeting tone analysis by worker agent."""

    overall_sentiment: Literal["positive", "neutral", "negative", "mixed"] = Field(
        default="neutral"
    )
    energy_level: Literal["high", "medium", "low"] = Field(default="medium")
    collaboration_quality: Literal["excellent", "good", "fair", "poor"] = Field(default="good")
    notes: str | None = Field(None, description="Additional observations about tone")


class KeyInsights(BaseModel):
    """Key insights extracted by worker agent."""

    insights: list[str] = Field(default_factory=list, description="Important insights")
    patterns: list[str] = Field(default_factory=list, description="Patterns observed")
    recommendations: list[str] = Field(
        default_factory=list, description="Recommendations based on the meeting"
    )


class TranscriptAnalysis(BaseModel):
    """Complete analysis aggregated by manager agent."""

    source_file: str = Field(..., description="Original transcript filename")
    processed_at: datetime = Field(description="When analysis was completed")
    summary: Summary
    action_points: ActionPoints
    todo_list: TodoList
    important_mentions: ImportantMentions
    recap: Recap
    meeting_tone: MeetingTone
    key_insights: KeyInsights
