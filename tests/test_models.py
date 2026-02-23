"""Test Pydantic models."""

from datetime import datetime, timezone

from meetingmind.models import (
    ActionPoint,
    ActionPoints,
    ImportantMention,
    ImportantMentions,
    KeyInsights,
    MeetingMetadata,
    MeetingTone,
    Recap,
    Summary,
    TodoItem,
    TodoList,
    TranscriptAnalysis,
)


def test_summary_model(subtests):
    """Test Summary model."""
    summary = Summary(content="Meeting summary", key_topics=["Topic 1", "Topic 2"])

    with subtests.test("content"):
        assert summary.content == "Meeting summary"

    with subtests.test("key_topics"):
        assert len(summary.key_topics) == 2
        assert "Topic 1" in summary.key_topics


def test_action_point_model(subtests):
    """Test ActionPoint model with all fields."""
    action = ActionPoint(
        description="Complete the report",
        owner="John",
        deadline="2024-01-15",
        priority="high",
    )

    with subtests.test("description"):
        assert action.description == "Complete the report"

    with subtests.test("owner"):
        assert action.owner == "John"

    with subtests.test("deadline"):
        assert action.deadline == "2024-01-15"

    with subtests.test("priority"):
        assert action.priority == "high"


def test_action_point_defaults(subtests):
    """Test ActionPoint model defaults."""
    action = ActionPoint(description="Do something")

    with subtests.test("owner_default"):
        assert action.owner is None

    with subtests.test("deadline_default"):
        assert action.deadline is None

    with subtests.test("priority_default"):
        assert action.priority == "medium"


def test_action_points_model(subtests):
    """Test ActionPoints container model."""
    actions = ActionPoints(
        items=[
            ActionPoint(description="Task 1", priority="high"),
            ActionPoint(description="Task 2", priority="low"),
        ]
    )

    with subtests.test("item_count"):
        assert len(actions.items) == 2

    with subtests.test("first_item"):
        assert actions.items[0].description == "Task 1"


def test_todo_item_model(subtests):
    """Test TodoItem model."""
    todo = TodoItem(task="Review PR", context="High priority PR from team")

    with subtests.test("task"):
        assert todo.task == "Review PR"

    with subtests.test("context"):
        assert todo.context == "High priority PR from team"


def test_important_mention_model(subtests):
    """Test ImportantMention model."""
    mention = ImportantMention(
        person="CEO", context="Mentioned in Q4 review", significance="Strategic decision maker"
    )

    with subtests.test("person"):
        assert mention.person == "CEO"

    with subtests.test("context"):
        assert mention.context == "Mentioned in Q4 review"

    with subtests.test("significance"):
        assert mention.significance == "Strategic decision maker"


def test_recap_model(subtests):
    """Test Recap model."""
    recap = Recap(
        highlights=["Successful launch", "Team performance"],
        decisions_made=["Hire 2 developers"],
        next_steps=["Schedule follow-up"],
    )

    with subtests.test("highlights"):
        assert len(recap.highlights) == 2

    with subtests.test("decisions_made"):
        assert recap.decisions_made[0] == "Hire 2 developers"

    with subtests.test("next_steps"):
        assert len(recap.next_steps) == 1


def test_meeting_tone_model(subtests):
    """Test MeetingTone model."""
    tone = MeetingTone(
        overall_sentiment="positive",
        energy_level="high",
        collaboration_quality="excellent",
        notes="Great team synergy",
    )

    with subtests.test("sentiment"):
        assert tone.overall_sentiment == "positive"

    with subtests.test("energy"):
        assert tone.energy_level == "high"

    with subtests.test("collaboration"):
        assert tone.collaboration_quality == "excellent"

    with subtests.test("notes"):
        assert tone.notes == "Great team synergy"


def test_meeting_tone_defaults(subtests):
    """Test MeetingTone model defaults."""
    tone = MeetingTone()

    with subtests.test("sentiment_default"):
        assert tone.overall_sentiment == "neutral"

    with subtests.test("energy_default"):
        assert tone.energy_level == "medium"

    with subtests.test("collaboration_default"):
        assert tone.collaboration_quality == "good"


def test_key_insights_model(subtests):
    """Test KeyInsights model."""
    insights = KeyInsights(
        insights=["Market opportunity identified"],
        patterns=["Consistent delay in deliveries"],
        recommendations=["Implement CI/CD pipeline"],
    )

    with subtests.test("insights"):
        assert len(insights.insights) == 1

    with subtests.test("patterns"):
        assert "delay" in insights.patterns[0]

    with subtests.test("recommendations"):
        assert "CI/CD" in insights.recommendations[0]


def test_transcript_analysis_model(subtests):
    """Test complete TranscriptAnalysis model."""
    analysis = TranscriptAnalysis(
        source_file="meeting.txt",
        processed_at=datetime(2024, 1, 15, 10, 30),
        summary=Summary(content="Summary", key_topics=["Topic"]),
        action_points=ActionPoints(items=[]),
        todo_list=TodoList(items=[]),
        important_mentions=ImportantMentions(items=[]),
        recap=Recap(),
        meeting_tone=MeetingTone(),
        key_insights=KeyInsights(),
    )

    with subtests.test("source_file"):
        assert analysis.source_file == "meeting.txt"

    with subtests.test("processed_at"):
        assert analysis.processed_at.year == 2024

    with subtests.test("summary"):
        assert analysis.summary.content == "Summary"

    with subtests.test("has_all_sections"):
        assert hasattr(analysis, "action_points")
        assert hasattr(analysis, "todo_list")
        assert hasattr(analysis, "important_mentions")
        assert hasattr(analysis, "recap")
        assert hasattr(analysis, "meeting_tone")
        assert hasattr(analysis, "key_insights")


def test_meeting_metadata_when_valid_data_then_creates_model(subtests):
    """Test MeetingMetadata model with valid data."""
    metadata = MeetingMetadata(
        title="Q4 Planning Meeting",
        meeting_datetime=datetime(2024, 3, 15, 10, 30, tzinfo=timezone.utc),
    )

    with subtests.test("title"):
        assert metadata.title == "Q4 Planning Meeting"

    with subtests.test("meeting_datetime"):
        assert metadata.meeting_datetime == datetime(2024, 3, 15, 10, 30, tzinfo=timezone.utc)

    with subtests.test("meeting_datetime_has_timezone"):
        assert metadata.meeting_datetime.tzinfo is not None


def test_meeting_metadata_when_no_datetime_then_defaults_to_none(subtests):
    """Test MeetingMetadata model defaults to None for meeting_datetime."""
    metadata = MeetingMetadata(title="Sprint Retrospective")

    with subtests.test("title"):
        assert metadata.title == "Sprint Retrospective"

    with subtests.test("meeting_datetime_default"):
        assert metadata.meeting_datetime is None


def test_transcript_analysis_when_metadata_provided_then_includes_metadata(subtests):
    """Test TranscriptAnalysis includes metadata when provided."""
    metadata = MeetingMetadata(
        title="Team Sync",
        meeting_datetime=datetime(2024, 3, 15, 10, 30, tzinfo=timezone.utc),
    )

    analysis = TranscriptAnalysis(
        source_file="meeting.txt",
        processed_at=datetime(2024, 3, 15, 11, 0, tzinfo=timezone.utc),
        summary=Summary(content="Summary", key_topics=["Topic"]),
        action_points=ActionPoints(items=[]),
        todo_list=TodoList(items=[]),
        important_mentions=ImportantMentions(items=[]),
        recap=Recap(),
        meeting_tone=MeetingTone(),
        key_insights=KeyInsights(),
        metadata=metadata,
    )

    with subtests.test("has_metadata"):
        assert analysis.metadata is not None

    with subtests.test("metadata_title"):
        assert analysis.metadata.title == "Team Sync"

    with subtests.test("metadata_datetime"):
        assert analysis.metadata.meeting_datetime == datetime(
            2024, 3, 15, 10, 30, tzinfo=timezone.utc
        )


def test_transcript_analysis_when_no_metadata_then_metadata_is_none(subtests):
    """Test TranscriptAnalysis metadata defaults to None."""
    analysis = TranscriptAnalysis(
        source_file="meeting.txt",
        processed_at=datetime(2024, 3, 15, 11, 0, tzinfo=timezone.utc),
        summary=Summary(content="Summary", key_topics=["Topic"]),
        action_points=ActionPoints(items=[]),
        todo_list=TodoList(items=[]),
        important_mentions=ImportantMentions(items=[]),
        recap=Recap(),
        meeting_tone=MeetingTone(),
        key_insights=KeyInsights(),
    )

    with subtests.test("metadata_is_none"):
        assert analysis.metadata is None
