# notebooks/data_prep.py
import pandas as pd
from pathlib import Path

# Robust pathing: Resolves the exact location of this file, then goes up to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
input_path = DATA_DIR / "ocpp_dataset.csv"

def inspect_dataset():
    if not input_path.exists():
        print(f"Error: Could not find dataset at {input_path}")
        return

    print(f"Loading dataset from: {input_path}")
    print("This may take a moment due to the file size (approx. 300MB+)...")
    
    # Load data
    df = pd.read_csv(input_path)
    
    print("\n" + "="*40)
    print(" DATASET INSPECTION REPORT ")
    print("="*40)
    
    # 1. Shape & Memory
    print(f"\n[1] SHAPE & MEMORY")
    print(f"Total Rows: {df.shape[0]:,}")
    print(f"Total Columns: {df.shape[1]}")
    memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    print(f"Memory Usage: ~{memory_mb:.2f} MB")
    
    # 2. Missing Values
    print(f"\n[2] MISSING & INFINITE VALUES")
    missing_counts = df.isnull().sum()
    missing_cols = missing_counts[missing_counts > 0]
    if missing_cols.empty:
        print("No missing values found.")
    else:
        print("Columns with missing values:")
        print(missing_cols)
        
    # 3. Duplicate Rows
    print(f"\n[3] DUPLICATE ROWS")
    duplicate_count = df.duplicated().sum()
    print(f"Total Duplicate Rows: {duplicate_count:,} ({(duplicate_count/len(df))*100:.2f}%)")
    
    # 4. Label Distribution
    print(f"\n[4] LABEL DISTRIBUTION")
    if 'Label' in df.columns:
        label_counts = df['Label'].value_counts()
        label_pct = df['Label'].value_counts(normalize=True) * 100
        dist_df = pd.DataFrame({'Count': label_counts, 'Percentage': label_pct})
        print(dist_df.round(4))
    else:
        print("Warning: 'Label' column not found! Check column names.")

    # 5. Data Types & Column Preview
    print(f"\n[5] COLUMN DATA TYPES")
    print(df.dtypes.value_counts())
    print("\nFirst 15 Columns:")
    print(df.columns.tolist()[:15])

if __name__ == "__main__":
    inspect_dataset()