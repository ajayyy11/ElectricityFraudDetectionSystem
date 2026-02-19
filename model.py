from sklearn.linear_model import LogisticRegression
import numpy as np
import joblib

# Sample training data
X = np.array([
    [100], [120], [150], [200], [250],
    [400], [450], [500], [600], [700]
])

# 0 = Normal, 1 = Fraud
y = np.array([0,0,0,0,0,1,1,1,1,1])

model = LogisticRegression()
model.fit(X, y)

joblib.dump(model, "fraud_model.pkl")

print("Model trained and saved.")
