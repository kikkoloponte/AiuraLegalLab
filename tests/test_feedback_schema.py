"""Test per FeedbackRequest e HistoryEntry (Pydantic)."""
import pytest
from pydantic import ValidationError

from aiura_legal.api.schemas import FeedbackRequest, HistoryEntry, FEEDBACK_ALLOWED_TAGS


# ---------------------------------------------------------------------------
# FeedbackRequest
# ---------------------------------------------------------------------------

def test_feedback_request_valid_minimal():
    req = FeedbackRequest(rating=3, tags=[])
    assert req.rating == 3
    assert req.tags == []
    assert req.note is None


def test_feedback_request_valid_full():
    req = FeedbackRequest(rating=5, tags=["Utile", "Citazioni corrette"], note="Ottima risposta")
    assert req.rating == 5
    assert "Utile" in req.tags
    assert req.note == "Ottima risposta"


def test_feedback_request_invalid_rating_too_high():
    with pytest.raises(ValidationError):
        FeedbackRequest(rating=6, tags=[])


def test_feedback_request_invalid_rating_zero():
    with pytest.raises(ValidationError):
        FeedbackRequest(rating=0, tags=[])


def test_feedback_request_invalid_tag():
    with pytest.raises(ValidationError):
        FeedbackRequest(rating=3, tags=["TagInesistente"])


def test_feedback_request_dedup_tags():
    req = FeedbackRequest(rating=3, tags=["Utile", "Utile", "Parziale"])
    assert req.tags == ["Utile", "Parziale"]


def test_feedback_request_note_max_length():
    with pytest.raises(ValidationError):
        FeedbackRequest(rating=3, tags=[], note="x" * 501)


def test_feedback_request_note_exactly_500():
    req = FeedbackRequest(rating=3, tags=[], note="x" * 500)
    assert len(req.note) == 500


def test_feedback_allowed_tags_all_valid():
    """Tutti i tag del set fisso devono essere accettati."""
    req = FeedbackRequest(rating=1, tags=list(FEEDBACK_ALLOWED_TAGS))
    assert set(req.tags) == FEEDBACK_ALLOWED_TAGS


# ---------------------------------------------------------------------------
# HistoryEntry — retrocompatibilità campi opzionali
# ---------------------------------------------------------------------------

def test_history_entry_minimal():
    """HistoryEntry con soli campi obbligatori — i nuovi devono avere default."""
    entry = HistoryEntry(
        id="abc",
        query="test",
        workspace="ws",
        verdict="PASS",
        created_at="2026-06-05T10:00:00Z",
    )
    assert entry.answer == ""
    assert entry.analysis_sections == []
    assert entry.sources == []
    assert entry.feedback_rating is None
    assert entry.feedback_tags == []
    assert entry.feedback_at is None


def test_history_entry_with_feedback():
    entry = HistoryEntry(
        id="abc",
        query="test",
        workspace="ws",
        verdict="PASS",
        created_at="2026-06-05T10:00:00Z",
        feedback_rating=4,
        feedback_tags=["Utile"],
        feedback_note="Buona",
        feedback_at="2026-06-05T10:05:00Z",
    )
    assert entry.feedback_rating == 4
    assert entry.feedback_tags == ["Utile"]
