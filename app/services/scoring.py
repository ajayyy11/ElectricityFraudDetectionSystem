import math


def calculate_epi(current_usage, avg_usage, fraud_prob):
    values = (current_usage, avg_usage, fraud_prob)
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in values):
        raise TypeError("Usage and probability values must be numbers")
    if any(not math.isfinite(value) for value in values):
        raise ValueError("Usage and probability values must be finite")
    if current_usage < 0 or avg_usage < 0:
        raise ValueError("Usage values must be non-negative")
    if not 0 <= fraud_prob <= 1:
        raise ValueError("fraud_prob must be between 0 and 1")

    efficiency_score = max(0, 100 - abs(current_usage - avg_usage))
    risk_penalty = fraud_prob * 50
    epi = max(0, min(100, efficiency_score - risk_penalty))
    return round(epi, 2)


def monthly_change(current, previous):
    if not math.isfinite(current) or not math.isfinite(previous):
        raise ValueError("Usage values must be finite")
    if current < 0 or previous < 0:
        raise ValueError("Usage values must be non-negative")
    if previous == 0:
        return 0
    change = ((current - previous) / previous) * 100
    return round(change, 2)
