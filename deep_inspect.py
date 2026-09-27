import pandas as pd
import os

def deep_inspect(file_path):
    print(f"\n{'#'*50}")
    print(f"🔍 ANALYZING: {os.path.basename(file_path)}")
    print(f"{'#'*50}")

    if not os.path.exists(file_path):
        print(f"❌ ERROR: File not found at {file_path}")
        return

    try:
        # 1. Fast Row Count (Memory Efficient)
        print("--- 1. Scale ---")
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            row_count = sum(1 for line in f) - 1
        print(f"Total Rows: {row_count:,}")

        # 2. Structure & Samples (Read first 100 rows for a good sample)
        print("\n--- 2. Structure & Samples ---")
        df = pd.read_csv(file_path, sep='\t', nrows=100)
        print(f"Columns found: {list(df.columns)}")
        print("\nFirst 5 rows sample:")
        print(df.head().to_string())

        # 3. Data Quality (Nulls and Types)
        print("\n--- 3. Data Quality (Sample Analysis) ---")
        info_df = pd.DataFrame({
            'Type': df.dtypes,
            'Nulls_in_sample': df.isnull().sum(),
            'Unique_in_sample': df.nunique()
        })
        print(info_df)

        # 4. Specific Column Checks (Pattern Recognition)
        # We check for common patterns in the name and address columns
        print("\n--- 4. Pattern Analysis (Sample) ---")
        for col in df.columns:
            if 'name' in col.lower() or 'address' in col.lower():
                print(f"\n[{col.upper()} patterns]")
                # Show how many rows have very short or very long strings
                lengths = df[col].astype(str).str.len()
                print(f"  Avg Length: {lengths.mean():.2f}")
                print(f"  Min Length: {lengths.min()}")
                print(f"  Max Length: {lengths.max()}")
                print(f"  Empty/NaN count in sample: {df[col].isnull().sum()}")

        # 5. Country Check (Special handling for the 'France' trap)
        if 'country' in df.columns:
            print("\n--- 5. Country Distribution (Sample) ---")
            print(df['country'].value_counts())

    except Exception as e:
        print(f"❌ FATAL ERROR reading {file_path}: {e}")

# --- CONFIGURATION ---
# Adjust these paths if your folder names are different
dataset_root = "Dataset/student_resource/dataset"

files_to_inspect = [
    f"{dataset_root}/train/train_source1.tsv",
    f"{dataset_root}/train/train_source2.tsv",
    f"{dataset_root}/train/train_source3.tsv",
    f"{dataset_root}/train/train_ground_truth.tsv",
    f"{dataset_root}/test/test_source1.tsv",
    f"{dataset_root}/test/test_source2.tsv",
    f"{dataset_root}/test/test_source3.tsv"
]

if __name__ == "__main__":
    for f in files_to_inspect:
        deep_inspect(f)
    print(f"\n\n{'='*50}")
    print("✅ INSPECTION COMPLETE")
    print("PLEASE COPY THE TEXT ABOVE AND PASTE IT HERE.")
    print(f"{'='*50}")