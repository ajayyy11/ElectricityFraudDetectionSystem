import os
import joblib
import logging
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
        if self._model is None:
            try:
                base_path = os.path.dirname(__file__)
                self._model = joblib.load(os.path.join(base_path, "ml_models", "fraud_model.pkl"))
                self._scaler = joblib.load(os.path.join(base_path, "ml_models", "scaler.pkl"))
                logging.info("ML Resources loaded successfully.")
            except Exception as e:
                logging.error(f"Failed to load ML resources: {e}")
                raise RuntimeError("ML system unavailable")

    def predict_and_save(self, user_id, current_usage, avg_usage):
        self._load_resources()
        
        # 1. Data Validation
        if current_usage < 0 or avg_usage < 0:
            raise ValueError("Usage values must be non-negative")

        # 2. Prediction
        usage_ratio = current_usage / avg_usage if avg_usage > 0 else 1
        variability = abs(current_usage - avg_usage)
        
        scaled_input = self._scaler.transform([[current_usage, avg_usage, usage_ratio, variability]])
        fraud_probability = float(self._model.predict_proba(scaled_input)[0][1])

        # 3. Decision Logic & Explanation
        epi = calculate_epi(current_usage, avg_usage, fraud_probability)
        anomaly_status = detect_anomaly(current_usage, avg_usage)
        reason = self.generate_explanation(current_usage, avg_usage, fraud_probability, anomaly_status)

        # 4. Persistence
        new_record = EnergyRecord(
            usage=current_usage,
            avg_usage=avg_usage,
            fraud_probability=fraud_probability,
            epi_score=epi,
            anomaly_status=anomaly_status,
            reason=reason,
            user_id=user_id
        )
        db.session.add(new_record)
        db.session.commit()
        return new_record

    def generate_explanation(self, usage, avg, prob, status):
        """Generate a human-readable reason for the AI's decision."""
        if prob <= 0.2:
            return "Usage patterns are consistent with historical data. No anomalies detected."
        
        reasons = []
        delta_pct = ((usage - avg) / avg * 100) if avg > 0 else 0
        
        if delta_pct > 30:
            reasons.append(f"Significant consumption spike ({round(delta_pct, 1)}% above average)")
        elif delta_pct < -30:
            reasons.append(f"Unusual consumption drop ({round(abs(delta_pct), 1)}% below average)")
            
        if prob > 0.6:
            reasons.append("ML model identified multiple correlation vectors matching known fraud signatures.")
        elif prob > 0.3:
            reasons.append("Consumption variability indicates irregular load profile.")
            
        return " - ".join(reasons) if reasons else "Pattern deviation detected by neural analysis."

ml_engine = MLEngine()
