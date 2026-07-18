
from vidsift.features.validation.decision_engine import DecisionEngine
from vidsift.models.validation.metadata_validation_result import \
    MetadataValidationResult
from vidsift.models.validation.transcript_validation_result import \
    TranscriptValidationResult
from vidsift.models.video import Video

# Metadata validation test cases

metadata_perfect_match = MetadataValidationResult(
    metadata_score=3,
    topic_match_score=3,
    confidence=3,
    flags=set(),
    summary_reason=""
)

metadata_low_metadata_score = MetadataValidationResult(
    metadata_score=1,
    topic_match_score=3,
    confidence=3,
    flags=set(),
    summary_reason=""
)

metadata_low_topic_match = MetadataValidationResult(
    metadata_score=3,
    topic_match_score=1,
    confidence=3,
    flags={"low_topic_match"},
    summary_reason=""
)

metadata_low_confidence = MetadataValidationResult(
    metadata_score=3,
    topic_match_score=3,
    confidence=1,
    flags=set(),
    summary_reason=""
)

metadata_fake_urgency = MetadataValidationResult(
    metadata_score=2,
    topic_match_score=3,
    confidence=3,
    flags={"fake_urgency"},
    summary_reason=""
)

metadata_excessive_hype = MetadataValidationResult(
    metadata_score=2,
    topic_match_score=3,
    confidence=3,
    flags={"excessive_hype"},
    summary_reason=""
)

metadata_sensationalism = MetadataValidationResult(
    metadata_score=2,
    topic_match_score=3,
    confidence=3,
    flags={"sensationalism"},
    summary_reason=""
)

metadata_spam_tone = MetadataValidationResult(
    metadata_score=1,
    topic_match_score=2,
    confidence=3,
    flags={"spam_tone"},
    summary_reason=""
)

metadata_suspicious_certainty = MetadataValidationResult(
    metadata_score=2,
    topic_match_score=3,
    confidence=2,
    flags={"suspicious_certainty"},
    summary_reason=""
)

metadata_many_negative_flags = MetadataValidationResult(
    metadata_score=1,
    topic_match_score=1,
    confidence=2,
    flags={
        "fake_urgency",
        "excessive_hype",
        "sensationalism",
        "spam_tone",
        "suspicious_certainty",
        "low_topic_match",
    },
    summary_reason=""
)


# Transcript validation test cases

transcript_perfect_content = TranscriptValidationResult(
    content_quality_score=3,
    topic_match_score=3,
    confidence=3,
    flags=set(),
    summary_reason=""
)

transcript_low_content_quality = TranscriptValidationResult(
    content_quality_score=1,
    topic_match_score=3,
    confidence=3,
    flags={"low_substance"},
    summary_reason=""
)

transcript_low_topic_match = TranscriptValidationResult(
    content_quality_score=3,
    topic_match_score=1,
    confidence=3,
    flags={"off_topic"},
    summary_reason=""
)

transcript_low_confidence = TranscriptValidationResult(
    content_quality_score=3,
    topic_match_score=3,
    confidence=1,
    flags=set(),
    summary_reason=""
)

transcript_self_promotion = TranscriptValidationResult(
    content_quality_score=2,
    topic_match_score=3,
    confidence=3,
    flags={"excessive_self_promotion"},
    summary_reason=""
)

transcript_fear_mongering = TranscriptValidationResult(
    content_quality_score=2,
    topic_match_score=3,
    confidence=3,
    flags={"fear_mongering"},
    summary_reason=""
)

transcript_manipulative = TranscriptValidationResult(
    content_quality_score=1,
    topic_match_score=3,
    confidence=3,
    flags={"manipulative_persuasion"},
    summary_reason=""
)

transcript_repetitive = TranscriptValidationResult(
    content_quality_score=2,
    topic_match_score=3,
    confidence=2,
    flags={"repetitive_content"},
    summary_reason=""
)

transcript_multiple_quality_issues = TranscriptValidationResult(
    content_quality_score=1,
    topic_match_score=2,
    confidence=2,
    flags={
        "low_substance",
        "excessive_self_promotion",
        "repetitive_content",
    },
    summary_reason=""
)

transcript_all_negative_flags = TranscriptValidationResult(
    content_quality_score=1,
    topic_match_score=1,
    confidence=1,
    flags={
        "low_substance",
        "excessive_self_promotion",
        "fear_mongering",
        "manipulative_persuasion",
        "off_topic",
        "repetitive_content",
    },
    summary_reason=""
)



def test_decision_engine_downloads_perfect_match():
    engine = DecisionEngine(
        metadata_perfect_match,
        transcript_perfect_content,
    )

    scores = engine.calculate_decision_scores()
    result = engine.make_decision(scores)

    assert result.decision == "downloaded"
    assert result.topic_match_score == 3.0
    assert result.content_quality_score == 3.0


def test_decision_engine_downloads_high_quality_but_medium_topic_match():
    engine = DecisionEngine(
        metadata_low_topic_match,
        transcript_perfect_content,
    )

    scores = engine.calculate_decision_scores()
    result = engine.make_decision(scores)

    assert result.decision == "downloaded"


def test_decision_engine_discards_low_scores():
    engine = DecisionEngine(
        metadata_low_metadata_score,
        transcript_low_content_quality,
    )

    scores = engine.calculate_decision_scores()
    result = engine.make_decision(scores)

    assert result.decision == "discarded"


def test_decision_engine_discards_low_topic_match():
    engine = DecisionEngine(
        metadata_many_negative_flags,
        transcript_all_negative_flags,
    )

    scores = engine.calculate_decision_scores()
    result = engine.make_decision(scores)

    assert result.decision == "discarded"


def test_decision_engine_discards_borderline_scores():
    engine = DecisionEngine(
        metadata_low_topic_match,
        transcript_low_content_quality,
    )

    scores = engine.calculate_decision_scores()
    result = engine.make_decision(scores)

    assert result.decision == "discarded"


def test_decision_engine_calculates_weighted_scores_correctly():
    engine = DecisionEngine(
        metadata_perfect_match,
        transcript_low_content_quality,
    )

    scores = engine.calculate_decision_scores()

    assert scores["topic_match_score"] == 3.0
    assert scores["quality_score"] == 1.4


def test_decision_engine_preserves_validation_context_in_result():
    engine = DecisionEngine(
        metadata_fake_urgency,
        transcript_manipulative,
    )

    scores = engine.calculate_decision_scores()
    result = engine.make_decision(scores)

    assert "fake_urgency" in result.summary_reason["metadata"]["flags"]
    assert "manipulative_persuasion" in result.summary_reason["transcript"]["flags"]
