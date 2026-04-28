import pytest
from services.ml_engine import ml_engine

def test_explanation_logic():
    # Test normal usage
    exp = ml_engine.generate_explanation(400, 410, 0.1, "Normal")
    assert "consistent with historical data" in exp

    # Test spike usage
    exp = ml_engine.generate_explanation(600, 400, 0.8, "Spike")
    assert "spike" in exp.lower()
    assert "match" in exp.lower()

def test_data_validation():
    with pytest.raises(ValueError):
        ml_engine.predict_and_save(1, -10, 400)
