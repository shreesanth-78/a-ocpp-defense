# notebooks/train_baseline.py
import time
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

# Define Project Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_PATH = DATA_DIR / "train_balanced.csv"
TEST_PATH = DATA_DIR / "test_unbalanced.csv"
MODEL_SAVE_PATH = MODELS_DIR / "baseline_xgb.joblib"
ENCODER_SAVE_PATH = MODELS_DIR / "label_encoder.joblib"
FEATURES_SAVE_PATH = MODELS_DIR / "feature_columns.joblib"


def train_and_evaluate():
    print("=" * 60)
    print(" PHASE 5: BASELINE ML DETECTOR TRAINING & EVALUATION ")
    print("=" * 60)

    # 1. Load Data
    print(f"\n[1] Loading balanced training data from: {TRAIN_PATH}")
    train_df = pd.read_csv(TRAIN_PATH)

    print(f"[2] Loading untouched test data from: {TEST_PATH}")
    test_df = pd.read_csv(TEST_PATH)

    # 2. Separate Features & Labels
    X_train = train_df.drop("Label", axis=1)
    y_train_raw = train_df["Label"]

    X_test = test_df.drop("Label", axis=1)
    y_test_raw = test_df["Label"]

    # Save feature names to ensure future inference matches exact column order
    feature_columns = list(X_train.columns)
    joblib.dump(feature_columns, FEATURES_SAVE_PATH)
    print(f"Saved {len(feature_columns)} feature names to: {FEATURES_SAVE_PATH}")

    # 3. Label Encoding
    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(y_train_raw)
    y_test = label_encoder.transform(y_test_raw)

    joblib.dump(label_encoder, ENCODER_SAVE_PATH)
    print(f"Saved LabelEncoder with {len(label_encoder.classes_)} classes to: {ENCODER_SAVE_PATH}")

    # 4. Model Training (XGBoost)
    print("\n[3] Training XGBoost Classifier...")
    xgb_model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        tree_method="hist",  # Fast histogram-based method
        random_state=42,
        n_jobs=-1,
        eval_metric="mlogloss",
    )

    start_train = time.time()
    xgb_model.fit(X_train, y_train)
    train_duration = time.time() - start_train
    print(f"Training completed in {train_duration:.2f} seconds.")

    # 5. Model Inference on Test Set
    print("\n[4] Evaluating on untouched Test Set (255k+ rows)...")
    start_infer = time.time()
    y_pred = xgb_model.predict(X_test)
    infer_duration = time.time() - start_infer
    avg_latency_ms = (infer_duration / len(X_test)) * 1000

    # 6. Performance Metrics
    print("\n" + "=" * 60)
    print(" BASELINE PERFORMANCE METRICS ")
    print("=" * 60)
    print(f"Total Test Samples: {len(X_test):,}")
    print(f"Inference Latency: {avg_latency_ms:.4f} ms per sample")

    # Overall Metrics
    macro_f1 = f1_score(y_test, y_pred, average="macro")
    weighted_f1 = f1_score(y_test, y_pred, average="weighted")
    print(f"Macro F1-Score:    {macro_f1:.4f}")
    print(f"Weighted F1-Score: {weighted_f1:.4f}")

    # Detailed Classification Report
    print("\n--- Detailed Classification Report ---")
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=label_encoder.classes_,
            digits=4,
            zero_division=0,
        )
    )

    # 7. False Positive Rate on Benign Class
    benign_idx = np.where(label_encoder.classes_ == "Benign")[0]
    if len(benign_idx) > 0:
        b_idx = benign_idx[0]
        cm = confusion_matrix(y_test, y_pred)
        benign_total = cm[b_idx].sum()
        benign_correct = cm[b_idx, b_idx]
        benign_fp = benign_total - benign_correct
        fp_rate = (benign_fp / benign_total) * 100 if benign_total > 0 else 0
        print(f"Benign False Positive Rate (FPR): {fp_rate:.2f}% ({benign_fp}/{benign_total} benign misclassified as attack)")

    # 8. Save Trained Model
    joblib.dump(xgb_model, MODEL_SAVE_PATH)
    print(f"\n[5] Model artifact successfully saved to: {MODEL_SAVE_PATH}")


if __name__ == "__main__":
    train_and_evaluate()