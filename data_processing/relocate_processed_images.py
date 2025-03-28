import os
import pandas as pd
import shutil

METADATA_CSV = "data_processing/metadata_refined.csv"
ORIGINAL_IMAGE_ROOT = "data_processing/processed_images"
OUTPUT_ROOT = "data_processing/processed_images_canonical"

os.makedirs(OUTPUT_ROOT, exist_ok=True)

df = pd.read_csv(METADATA_CSV)
df = df.dropna(subset=["filename", "canonical_label"])

moved = 0
missing = 0

for _, row in df.iterrows():
    old_path = None
    for subdir in os.listdir(ORIGINAL_IMAGE_ROOT):
        candidate = os.path.join(ORIGINAL_IMAGE_ROOT, subdir, row["filename"])
        if os.path.exists(candidate):
            old_path = candidate
            break

    if not old_path:
        print(f"❌ Missing file: {row['filename']}")
        missing += 1
        continue

    target_dir = os.path.join(OUTPUT_ROOT, row["canonical_label"])
    os.makedirs(target_dir, exist_ok=True)

    target_path = os.path.join(target_dir, row["filename"])
    shutil.copy2(old_path, target_path)
    moved += 1

print(f"✅ Moved {moved} files to canonical directories.")
print(f"⚠️ Missing {missing} files.")
