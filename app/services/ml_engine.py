import logging
import math
import os

import joblib
from app.models import db, EnergyRecord
from app.services.scoring import calculate_epi
from app.services.prediction import detect_anomaly


class MLEngine:
    _instance = None
    _model = None
    _scaler = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLEngine, cls).__new__(cls)
        return cls._instance

    def _load_resources(self):
        if self._model is None or self._scaler is None:
            try:
                base_path = os.path.dirname(__file__)
                model_path = os.path.join(base_path, "ml_models", "fraud_model.pkl")
                scaler_path = os.path.join(base_path, "ml_models", "scaler.pkl")
                self._model = joblib.load(model_path)
                self._scaler = joblib.load(scaler_path)
                if not hasattr(self._model, "predict_proba"):
                    raise TypeError("Fraud model must implement predict_proba")
                if not hasattr(self._scaler, "transform"):
                    raise TypeError("Feature scaler must implement transform")
                logging.info("ML resources loaded successfully.")
            except Exception as exc:
                self._model = None
                self._scaler = None
                logging.exception("Failed to load ML resources")
                raise RuntimeError("ML system unavailable; check model artifacts and dependencies.") from exc

    @staticmethod
    def _validate_usage(current_usage, avg_usage):
        for name, value in (("current_usage", current_usage), ("avg_usage", avg_usage)):
            if isinstance(value, bool):
                raise ValueError(f"{name} must be a finite, non-negative number")
            try:
                number = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{name} must be a finite, non-negative number") from exc
            if not math.isfinite(number) or number < 0:
                raise ValueError(f"{name} must be a finite, non-negative number")
        return float(current_usage), float(avg_usage)

    def predict_and_save(self, user_id, current_usage, avg_usage):
        # Validate before loading model artifacts or doing any database work.
        current_usage, avg_usage = self._validate_usage(current_usage, avg_usage)
        self._load_resources()

        usage_ratio = current_usage / avg_usage if avg_usage > 0 else 1.0
        variability = abs(current_usage - avg_usage)
        features = [[current_usage, avg_usage, usage_ratio, variability]]
        scaled_input = self._scaler.transform(features)
        probabilities = self._model.predict_proba(scaled_input)
        if len(probabilities) != 1 or len(probabilities[0]) < 2:
            raise RuntimeError("Fraud model returned an unexpected probability shape")
        fraud_probability = float(probabilities[0][1])
        if not math.isfinite(fraud_probability) or not 0 <= fraud_probability <= 1:
            raise RuntimeError("Fraud model returned an invalid probability")

        epi = calculate_epi(current_usage, avg_usage, fraud_probability)
        anomaly_status = detect_anomaly(current_usage, avg_usage)
        reason = self.generate_explanation(
            current_usage, avg_usage, fraud_probability, anomaly_status
        )

        new_record = EnergyRecord(
            usage=current_usage,
            avg_usage=avg_usage,
            fraud_probability=fraud_probability,
            epi_score=epi,
            anomaly_status=anomaly_status,
            reason=reason,
            user_id=user_id,
        )
        db.session.add(new_record)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return new_record

    def generate_explanation(self, usage, avg, prob, status):
        """Generate a concise explanation for a model prediction."""
        if prob <= 0.2:
            return "Usage patterns are consistent with historical data. No anomalies detected."

        reasons = []
        delta_pct = ((usage - avg) / avg * 100) if avg > 0 else 0

        if delta_pct > 30:
            reasons.append(f"Significant consumption spike ({round(delta_pct, 1)}% above average)")
        elif delta_pct < -30:
            reasons.append(f"Unusual consumption drop ({round(abs(delta_pct), 1)}% below average)")

        if prob > 0.6:
            reasons.append("The model assigned a high fraud-risk probability; review the underlying data.")
        elif prob > 0.3:
            reasons.append("Consumption variability indicates an irregular load profile.")

        return " - ".join(reasons) if reasons else "Pattern deviation detected; review the underlying data."


ml_engine = MLEngine()
