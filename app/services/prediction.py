def predict_next_usage(current_usage, avg_usage):
    """Predict next cycle usage using weighted trend factor."""
    trend_factor = (current_usage - avg_usage) * 0.4
    prediction = current_usage + trend_factor
    return round(max(0, prediction), 2)


def detect_anomaly(current_usage, avg_usage):
    """Detect anomaly using statistical deviation and ratio analysis."""
    if avg_usage <= 0:
        return "Initial baseline — normal"
    
    deviation = current_usage - avg_usage
    deviation_pct = (deviation / avg_usage) * 100
    
    if deviation_pct > 50:
        return "CRITICAL: Extreme usage surge"
    elif deviation_pct > 25:
        return "High deviation: Potential fraud"
    elif deviation_pct < -30:
        return "Significant drop: Potential meter tamper"
    elif abs(deviation_pct) > 10:
        return "Moderate fluctuation"
    else:
        return "Stable usage pattern"
