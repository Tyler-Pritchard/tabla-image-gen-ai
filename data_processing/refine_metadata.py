import os
import csv
import pandas as pd

# Input files
SCRAPER_METADATA = "data_collection/scraper/image_metadata.csv"
LABELER_METADATA = "data_training/metadata.csv"

# Output file
OUTPUT_FILE = "data_processing/metadata_refined.csv"

# Canonical labels
canonical_labels = {
    "dayan": ["dayan", "dayan_drum_right_hand"],
    "bayan": ["bayan", "bayan_drum_left_hand"],
    "set": ["tabla", "pair", "set", "tabla_set", "tabla drums", "tabla_pair", "tabla_image"],
    "playing_hands": ["hands", "close_up", "hand_playing", "tabla hands", "tabla playing up close"],
    "tabla_performance": ["performance", "on stage", "live", "concert", "player", "tabla performance", "tabla player on stage"],
    "not_tabla": ["snare", "drum kit", "drumset", "guitar", "music notation", "invalid", "other"]
}

def normalize_label(raw_label):
    raw_label = raw_label.lower()
    for canonical, variants in canonical_labels.items():
        if any(term in raw_label for term in variants):
            return canonical
    return "unknown"

def load_and_merge_metadata():
    frames = []

    if os.path.exists(SCRAPER_METADATA):
        df_scraper = pd.read_csv(SCRAPER_METADATA)
        if "Search Term" in df_scraper.columns:
            df_scraper = df_scraper.rename(columns={"Search Term": "category"})
        frames.append(df_scraper)

    if os.path.exists(LABELER_METADATA):
        df_labeler = pd.read_csv(LABELER_METADATA)
        frames.append(df_labeler)

    if frames:
        return pd.concat(frames, ignore_index=True)
    else:
        raise FileNotFoundError("No metadata CSV files found.")

def refine_and_save():
    df = load_and_merge_metadata()
    df["category"] = df["category"].astype(str)
    df["canonical_label"] = df["category"].apply(normalize_label)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Refined metadata saved to: {OUTPUT_FILE}")
    print(df["canonical_label"].value_counts())

if __name__ == "__main__":
    refine_and_save()
