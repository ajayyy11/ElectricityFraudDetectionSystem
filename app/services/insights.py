def generate_insight(current_usage, avg_usage, fraud_prob, predicted_usage):
    """Generate actionable AI insight based on real per-user metrics."""
    messages = []
    delta = current_usage - avg_usage

    # Usage vs baseline
    if delta > 0:
        messages.append(
            f"⚡ Current usage is {abs(round(delta, 1))} kWh above your personal average — "
            f"a {round(abs(delta)/avg_usage*100, 1)}% spike."
        )
    elif delta < 0:
        messages.append(
            f"✅ Current usage is {abs(round(delta, 1))} kWh below your personal average — "
            f"well within normal range."
        )
    else:
        messages.append("✅ Usage is exactly at your personal average. No deviations detected.")

    # Fraud risk level
    if fraud_prob > 0.5:
        messages.append(
            "🚨 HIGH RISK: Fraud probability exceeds 50%. Immediate review recommended."
        )
    elif fraud_prob > 0.25:
        messages.append(
            f"⚠️ ELEVATED RISK: Fraud probability is {round(fraud_prob*100, 1)}%. "
            "Irregular consumption pattern detected."
        )
    elif fraud_prob > 0.1:
        messages.append(
            f"🔶 Minor anomaly: Fraud probability at {round(fraud_prob*100, 1)}%. "
            "Monitor closely over the next cycle."
        )
    else:
        messages.append(
            f"🟢 LOW RISK: Consumption behaviour appears stable "
            f"(fraud probability: {round(fraud_prob*100, 1)}%)."
        )

    # Next cycle forecast
    if predicted_usage > current_usage * 1.05:
        messages.append(
            f"📈 Forecast: Next billing cycle projected at {predicted_usage} kWh — "
            "an increase. Consider reducing high-load appliances."
        )
    elif predicted_usage < current_usage * 0.95:
        messages.append(
            f"📉 Forecast: Next cycle projected at {predicted_usage} kWh — "
            "consumption expected to decrease or stabilise."
        )
    else:
        messages.append(
            f"📊 Forecast: Next cycle projected at {predicted_usage} kWh — "
            "similar to current usage."
        )

    return " ".join(messages)
