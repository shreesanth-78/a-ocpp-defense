# inspect_data.py
import pandas as pd
import os

dataset_path = os.path.join("data", "ocpp_dataset.csv")

if not os.path.exists(dataset_path):
    print(f"Error: Dataset not found at {dataset_path}")
else:
    print("Loading dataset...")
    df = pd.read_csv(dataset_path)
    
    print("\n--- Dataset Overview ---")
    print(f"Total Rows: {df.shape[0]}")
    print(f"Total Columns: {df.shape[1]}")
    
    print("\n--- First 10 Columns ---")
    print(df.columns[:10].tolist())
    
    # Assuming the target label is named 'Label' or similar. 
    # We will look for common label column names.
    label_cols = [col for col in df.columns if 'label' in col.lower() or 'class' in col.lower() or 'attack' in col.lower()]
    
    if label_cols:
        target = label_cols[-1]
        print(f"\n--- Detected Target Column: {target} ---")
        print("Class Distribution:")
        print(df[target].value_counts())
    else:
        print("\n--- No obvious 'Label' column detected. Please check the columns manually. ---")