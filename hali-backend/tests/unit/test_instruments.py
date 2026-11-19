import pytest
from app.services.triage.instruments import PHQ9Scorer, GAD7Scorer, AUDITCScorer


def test_phq9_scoring_minimal():
    scores = [0, 1, 0, 1, 0, 0, 1, 0, 0]
    res = PHQ9Scorer.validate_and_score(scores)
    assert res["total_score"] == 3
    assert res["severity"] == "Minimal"
    assert res["is_item_9_positive"] is False
    assert res["item_9_score"] == 0


def test_phq9_scoring_item9_positive():
    # Item 9 is positive (score = 1)
    scores = [1, 1, 1, 1, 0, 0, 1, 0, 1]
    res = PHQ9Scorer.validate_and_score(scores)
    assert res["item_9_score"] == 1
    assert res["is_item_9_positive"] is True


def test_phq9_invalid_item_count():
    with pytest.raises(ValueError, match="PHQ-9 requires exactly 9 items"):
        PHQ9Scorer.validate_and_score([1, 2, 3])


def test_phq9_invalid_score_range():
    with pytest.raises(ValueError, match="score '5' is invalid"):
        PHQ9Scorer.validate_and_score([1, 2, 3, 0, 1, 2, 5, 1, 0])


def test_gad7_scoring_severe():
    scores = [3, 3, 2, 3, 2, 3, 2]
    res = GAD7Scorer.validate_and_score(scores)
    assert res["total_score"] == 18
    assert res["severity"] == "Severe"


def test_gad7_invalid_count():
    with pytest.raises(ValueError, match="GAD-7 requires exactly 7 items"):
        GAD7Scorer.validate_and_score([1, 2, 3, 4])


def test_auditc_scoring_hazardous():
    scores = [2, 1, 2]  # Total 5 (>= 4 is Hazardous)
    res = AUDITCScorer.validate_and_score(scores)
    assert res["total_score"] == 5
    assert res["risk_level"] == "Hazardous"


def test_auditc_scoring_low():
    scores = [1, 0, 1]  # Total 2 (< 4 is Low)
    res = AUDITCScorer.validate_and_score(scores)
    assert res["total_score"] == 2
    assert res["risk_level"] == "Low"

