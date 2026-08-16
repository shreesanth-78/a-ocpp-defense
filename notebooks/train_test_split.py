# notebooks/train_test_split.py
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
input_path = DATA_DIR / "ocpp_dataset.csv"
train_path = DATA_DIR / "train_balanced.csv"
test_path = DATA_DIR / "test_unbalanced.csv"

def prepare_data():
    print(f"Loading dataset from: {input_path}")
    df = pd.read_csv(input_path)
    
    # 1. Clean data (Drop the 4 duplicate rows we found)
    df = df.drop_duplicates()
    
    # Separate features (X) and target (y)
    if 'Label' not in df.columns:
        print("Error: 'Label' column not found.")
        return
        
    X = df.drop('Label', axis=1)
    y = df['Label']
    
    # 2. Train/Test Split (80% train, 20% test)
    # stratify=y ensures the 82 benign rows are split proportionally (approx 65 train, 17 test)
    print("\nSplitting data into Train and Test sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    train_df = pd.concat([X_train, y_train], axis=1)
    test_df = pd.concat([X_test, y_test], axis=1)
    
    print(f"Original Training Set Size: {len(train_df)}")
    print(f"Original Test Set Size: {len(test_df)}")

    # 3. Balance ONLY the Training Data
    print("\nBalancing the Training Set...")
    sampled_dfs = []
    
    # Target counts for balancing the training set
    ATTACK_SAMPLE_SIZE = 2000
    BENIGN_SAMPLE_SIZE = 5000
    
    for label in train_df['Label'].unique():
        class_df = train_df[train_df['Label'] == label]
        
        if label == 'Benign':
            # Oversample Benign in training data
            upsampled = resample(class_df, replace=True, n_samples=BENIGN_SAMPLE_SIZE, random_state=42)
            sampled_dfs.append(upsampled)
        elif len(class_df) > ATTACK_SAMPLE_SIZE:
            # Undersample large attack classes in training data
            downsampled = resample(class_df, replace=False, n_samples=ATTACK_SAMPLE_SIZE, random_state=42)
            sampled_dfs.append(downsampled)
        else:
            # Keep small attack classes as is
            sampled_dfs.append(class_df)

    train_balanced_df = pd.concat(sampled_dfs)
    # Shuffle the training set
    train_balanced_df = train_balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print("\n--- Balanced Training Set Distribution ---")
    print(train_balanced_df['Label'].value_counts())
    
    # 4. Save the datasets
    print("\nSaving datasets...")
    train_balanced_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    print(f"Saved balanced training data to: {train_path}")
    print(f"Saved untouched test data to: {test_path}")

if __name__ == "__main__":
    prepare_data()