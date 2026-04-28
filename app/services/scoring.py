def calculate_epi(current_usage, avg_usage, fraud_prob):
    efficiency_score = max(0, 100 - abs(current_usage - avg_usage))
    risk_penalty = fraud_prob * 50
    epi = max(0, min(100, efficiency_score - risk_penalty))
    return round(epi, 2)


def monthly_change(current, previous):
    if previous == 0:
        return 0
    change = ((current - previous) / previous) * 100
    return round(change, 2)
