import pytest

from app.services.scoring import calculate_epi, monthly_change


@pytest.mark.parametrize("probability", [0, 0.25, 0.5, 0.75, 1])
def test_epi_is_bounded(probability):
    score = calculate_epi(100, 100, probability)
    assert 0 <= score <= 100


def test_epi_is_rounded_to_two_decimals():
    assert calculate_epi(100, 100, 0.5) == 75.0


def test_monthly_change_handles_zero_baseline():
    assert monthly_change(10, 0) == 0


def test_monthly_change_calculates_percentage():
    assert monthly_change(150, 100) == 50.0


def test_epi_rejects_non_finite_probability():
    # Invalid model probabilities should never be treated as valid scores.
    with pytest.raises((ValueError, TypeError)):
        calculate_epi(100, 100, float("nan"))
