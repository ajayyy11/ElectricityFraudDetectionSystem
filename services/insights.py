def generate_insight(current_usage, avg_usage, fraud_prob, predicted_usage):
    
    messages = []

    if current_usage > avg_usage:
        messages.append("Energy consumption is above monthly average.")
    else:
        messages.append("Energy consumption is below monthly average.")

    if fraud_prob > 0.25:
        messages.append("Risk profile elevated due to irregular pattern.")
    elif fraud_prob > 0.15:
        messages.append("Minor anomaly detected in consumption behavior.")
    else:
        messages.append("Consumption behavior appears stable.")

    if predicted_usage > current_usage:
        messages.append("Projected increase expected next billing cycle.")
    else:
        messages.append("Projected consumption likely to remain stable or decrease.")

    return " ".join(messages)
