import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from random import sample

# CONFIG
METADATA_PATH = "data_training/metadata.csv"
IMAGES_BASE_PATH = "data_processing/processed_images"
SAMPLES_PER_LABEL = 16  # 4x4 grid

def display_grid(label, image_paths):
    fig, axes = plt.subplots(4, 4, figsize=(8, 8))
    fig.suptitle(f"Preview: {label}", fontsize=16)
    for ax, img_path in zip(axes.flatten(), image_paths):
        try:
            if not os.path.exists(img_path):
                print(f"❌ File not found: {img_path}")
                ax.set_title("Missing file")
                ax.axis('off')
                continue

            img = mpimg.imread(img_path)
            ax.imshow(img)
            ax.axis('off')
        except Exception as e:
            ax.set_title("Load error")
            ax.axis('off')
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    plt.show()

def main():
    df = pd.read_csv(METADATA_PATH)
    
    # Drop rows where either column is missing
    df = df.dropna(subset=["canonical_label", "filename"])
    df["filename"] = df["filename"].str.strip()
    df["canonical_label"] = df["canonical_label"].str.strip()

    for label in df["canonical_label"].unique():
        label_df = df[df["canonical_label"] == label]
        
        sample_paths = []
        for _, row in label_df.iterrows():
            label_val = row["canonical_label"]
            file_val = row["filename"]
            if isinstance(label_val, str) and isinstance(file_val, str):
                sample_paths.append(os.path.join(IMAGES_BASE_PATH, label_val, file_val))

        if not sample_paths:
            print(f"⚠️ No valid images found for label: {label}")
            continue

        sample_paths = sample(sample_paths, min(SAMPLES_PER_LABEL, len(sample_paths)))
        display_grid(label, sample_paths)

if __name__ == "__main__":
    main()
