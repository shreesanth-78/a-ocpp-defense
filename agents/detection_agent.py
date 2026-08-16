import joblib
import pandas as pd
from pathlib import Path
import warnings

# Suppress XGBoost warnings for cleaner logs
warnings.filterwarnings("ignore", category=UserWarning)


class DetectionAgent:
    def __init__(self):
        # Load artifacts using project-relative paths
        self.project_root = Path(__file__).resolve().parent.parent
        self.models_dir = self.project_root / "models"

        # Load the model, encoder, and feature order
        self.model = joblib.load(self.models_dir / "baseline_xgb.joblib")
        self.label_encoder = joblib.load(
            self.models_dir / "label_encoder.joblib"
        )
        self.feature_columns = joblib.load(
            self.models_dir / "feature_columns.joblib"
        )

    def analyze(self, telemetry_data: dict) -> dict:
        """
        Takes a single dictionary of telemetry data, formats it for XGBoost,
        and returns a JSON-serializable detection report.
        """

        # Convert incoming dictionary to DataFrame
        df = pd.DataFrame([telemetry_data])

        # Ensure all required columns exist
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0

        # Reorder columns exactly as used during training
        df = df[self.feature_columns]

        # Predict probabilities and class
        probabilities = self.model.predict_proba(df)[0]
        predicted_idx = self.model.predict(df)[0]

        # Convert prediction index to a native Python integer
        predicted_idx = int(predicted_idx)

        # Convert predicted label to native Python string
        predicted_label = str(
            self.label_encoder.inverse_transform([predicted_idx])[0]
        )

        # Convert NumPy float32 → native Python float
        confidence = float(probabilities[predicted_idx] * 100)

        # Determine whether the prediction is an anomaly
        is_anomaly = bool(predicted_label != "Benign")

        # Build probability dictionary using native Python types
        probability_report = {
            str(self.label_encoder.classes_[i]): round(float(prob * 100), 2)
            for i, prob in enumerate(probabilities)
            if float(prob) > 0.01
        }

        # Return JSON-serializable structured output
        return {
            "predicted_label": predicted_label,
            "confidence": round(confidence, 2),
            "is_anomaly": is_anomaly,
            "probabilities": probability_report,
        }