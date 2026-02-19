def predict_next_usage(current_usage, avg_usage):
    # Simple predictive logic (can replace with ML later)
    trend_factor = (current_usage - avg_usage) * 0.5
    prediction = current_usage + trend_factor
    return round(prediction, 2)


def detect_anomaly(current_usage, avg_usage):
    deviation = abs(current_usage - avg_usage)
    if deviation > 40:
        return "High anomaly detected"
    elif deviation > 20:
        return "Moderate deviation observed"
    else:
        return "Usage within normal range"
