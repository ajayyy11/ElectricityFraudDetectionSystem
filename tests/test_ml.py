import math

import pytest

from app.services.ml_engine import MLEngine, ml_engine


@pytest.mark.parametrize(
    ("usage", "average"),
    [(400, 410), (600, 400), (0, 0)],
)
def test_explanation_is_a_string(usage, average):
    explanation = ml_engine.generate_explanation(usage, average, 0.1, "Normal")
    assert isinstance(explanation, str)
    assert explanation


def test_spike_explanation_mentions_spike_and_review():
    explanation = ml_engine.generate_explanation(600, 400, 0.8, "Spike").lower()
    assert "spike" in explanation
    assert "model" in explanation or "risk" in explanation


@pytest.mark.parametrize(
    ("usage", "average"),
    [
        (-1, 400),
        (400, -1),
        (float("nan"), 400),
        (400, float("inf")),
        (float("-inf"), 400),
        ("not-a-number", 400),
        (True, 400),
        (None, 400),
    ],
)
def test_invalid_usage_is_rejected_before_model_loading(monkeypatch, usage, average):
    engine = MLEngine()
    monkeypatch.setattr(
        engine, "_load_resources",
        lambda: pytest.fail("Model should not load for invalid input"),
    )
    with pytest.raises(ValueError):
        engine.predict_and_save(1, usage, average)


def test_valid_usage_is_normalized_to_float():
    assert MLEngine._validate_usage("12.5", "10") == (12.5, 10.0)
