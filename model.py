from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import numpy as np
import joblib
import random

# ===================================
# GENERATE REALISTIC TRAINING DATA
# ===================================

X = []
y = []

for _ in range(500):

    avg_usage = random.randint(380, 420)

    # Normal behavior (70%)
    if random.random() < 0.7:
        current_usage = avg_usage + random.randint(-30, 30)
        fraud = 0
    else:
        # Fraud behavior (30%)
        current_usage = avg_usage + random.randint(80, 200)
        fraud = 1

    X.append([current_usage, avg_usage])
    y.append(fraud)

X = np.array(X)
y = np.array(y)

# ===================================
# SCALE DATA
# ===================================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ===================================
# TRAIN MODEL
# ===================================
model = LogisticRegression()
model.fit(X_scaled, y)

# ===================================
# SAVE MODEL + SCALER
# ===================================
joblib.dump(model, "fraud_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("Realistic fraud model trained and saved successfully.")