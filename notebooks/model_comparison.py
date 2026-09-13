# notebooks/model_comparison.py
import time
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import f1_score, confusion_matrix, accuracy_score
import warnings

# Suppress convergence warnings from fast Logistic Regression testing
warnings.filterwarnings('ignore')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EVAL_DIR = PROJECT_ROOT / "evaluation"
EVAL_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_PATH = DATA_DIR / "train_balanced.csv"
TEST_PATH = DATA_DIR / "test_unbalanced.csv"
RESULTS_PATH = EVAL_DIR / "model_comparison_results.csv"

def run_comparison():
    print("=" * 70)
    print(" MODEL COMPARISON EXPERIMENT (AGENT 1 JUSTIFICATION) ")
    print("=" * 70)

    # 1. Load Data
    print("Loading datasets...")
    train_df = pd.read_csv(TRAIN_PATH)
    test_df = pd.read_csv(TEST_PATH)

    X_train = train_df.drop("Label", axis=1)
    y_train_raw = train_df["Label"]

    X_test = test_df.drop("Label", axis=1)
    y_test_raw = test_df["Label"]

    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(y_train_raw)
    y_test = label_encoder.transform(y_test_raw)
    
    benign_idx = np.where(label_encoder.classes_ == "Benign")[0]
    b_idx = benign_idx[0] if len(benign_idx) > 0 else -1

    # 2. Define the 4 Baselines
    models = {
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        "XGBoost": XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, tree_method="hist", random_state=42, n_jobs=-1, eval_metric="mlogloss")
    }

    results = []

    for name, model in models.items():
        print(f"\n--- Training {name} ---")
        
        # Train
        t0_train = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - t0_train
        
        # Inference
        t0_infer = time.time()
        y_pred = model.predict(X_test)
        infer_time = time.time() - t0_infer
        avg_latency_ms = (infer_time / len(X_test)) * 1000
        
        # Metrics
        acc = accuracy_score(y_test, y_pred)
        macro_f1 = f1_score(y_test, y_pred, average="macro")
        weighted_f1 = f1_score(y_test, y_pred, average="weighted")
        
        # FPR for Benign
        fpr = 0.0
        if b_idx != -1:
            cm = confusion_matrix(y_test, y_pred)
            benign_total = cm[b_idx].sum()
            benign_correct = cm[b_idx, b_idx]
            benign_fp = benign_total - benign_correct
            fpr = (benign_fp / benign_total) * 100 if benign_total > 0 else 0.0
            
        results.append({
            "Model": name,
            "Accuracy": round(acc, 4),
            "Macro_F1": round(macro_f1, 4),
            "Weighted_F1": round(weighted_f1, 4),
            "Benign_FPR_%": round(fpr, 4),
            "Latency_ms_per_sample": round(avg_latency_ms, 5),
            "Train_Time_sec": round(train_time, 2)
        })
        
        print(f"Macro F1: {macro_f1:.4f} | Benign FPR: {fpr:.2f}% | Latency: {avg_latency_ms:.5f} ms")

    # 3. Save Results
    results_df = pd.DataFrame(results)
    print("\n" + "=" * 70)
    print(" EXPERIMENT RESULTS ")
    print("=" * 70)
    print(results_df.to_string(index=False))
    
    results_df.to_csv(RESULTS_PATH, index=False)
    print(f"\nSaved benchmarking evidence to: {RESULTS_PATH}")

if __name__ == "__main__":
    run_comparison()