"""Evaluate saved fraud model artifacts against a labeled CSV.

Expected columns:
    current_usage, avg_usage, fraud_label

fraud_label must be the ground-truth binary class used during model training:
0 = non-fraud, 1 = fraud. This script does not train or alter the saved model.
"""
import argparse
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = PROJECT_ROOT / "app" / "services" / "ml_models"


def build_features(frame):
    current = pd.to_numeric(frame["current_usage"], errors="coerce")
    average = pd.to_numeric(frame["avg_usage"], errors="coerce")
    if current.isna().any() or average.isna().any():
        raise ValueError("Usage columns contain missing or non-numeric values.")
    if not np.isfinite(current).all() or not np.isfinite(average).all():
        raise ValueError("Usage columns contain non-finite values.")
    if (current < 0).any() or (average < 0).any():
        raise ValueError("Usage values must be non-negative.")
    ratio = np.where(average > 0, current / np.where(average > 0, average, 1), 1.0)
    variability = (current - average).abs()
    return pd.DataFrame({
        "current_usage": current,
        "avg_usage": average,
        "usage_ratio": ratio,
        "variability": variability,
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", help="CSV with current_usage, avg_usage, fraud_label columns")
    parser.add_argument("--threshold", type=float, default=0.5, help="Probability threshold (default: 0.5)")
    args = parser.parse_args()

    if not 0 < args.threshold < 1:
        parser.error("--threshold must be between 0 and 1")

    csv_path = Path(args.csv_path)
    if not csv_path.is_file():
        parser.error(f"CSV file not found: {csv_path}")

    try:
        data = pd.read_csv(csv_path)
        required = {"current_usage", "avg_usage", "fraud_label"}
        missing = required - set(data.columns)
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")
        labels = pd.to_numeric(data["fraud_label"], errors="raise").to_numpy()
        if len(labels) == 0 or not set(np.unique(labels)).issubset({0, 1}):
            raise ValueError("fraud_label must contain non-empty binary labels 0 and 1.")

        features = build_features(data)
        model = joblib.load(MODEL_DIR / "fraud_model.pkl")
        scaler = joblib.load(MODEL_DIR / "scaler.pkl")
        probabilities = model.predict_proba(scaler.transform(features))[:, 1]
        predictions = (probabilities >= args.threshold).astype(int)

        print(f"Rows evaluated: {len(labels)}")
        print(f"Threshold: {args.threshold:.2f}")
        print(f"Accuracy:  {accuracy_score(labels, predictions):.4f}")
        print(f"Precision: {precision_score(labels, predictions, zero_division=0):.4f}")
        print(f"Recall:    {recall_score(labels, predictions, zero_division=0):.4f}")
        print(f"F1 score:  {f1_score(labels, predictions, zero_division=0):.4f}")
        if len(np.unique(labels)) == 2:
            print(f"ROC-AUC:   {roc_auc_score(labels, probabilities):.4f}")
        else:
            print("ROC-AUC:   unavailable (evaluation labels contain only one class)")
        print("Confusion matrix [ [TN, FP], [FN, TP] ]:")
        print(confusion_matrix(labels, predictions, labels=[0, 1]))
        print("\nClassification report:")
        print(classification_report(labels, predictions, labels=[0, 1], zero_division=0))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Evaluation failed: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
