import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageEnhance
from tqdm import tqdm
import random

# Paths
METADATA_PATH = "data_collection/scraper/image_metadata.csv"
INPUT_ROOT = "data_collection/scraper/images"
OUTPUT_ROOT = "data_processing/processed_images"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "ESPCN_x2.pb")

# Canonical label mapping
LABEL_MAP = {
    "dayan_drum": "dayan",
    "dayan_drum_right_hand": "dayan",
    "bayan_drum": "bayan",
    "bayan_drum_left_hand": "bayan",
    "tabla_drums": "set",
    "tabla_drum_close-up": "set",
    "tabla_drum_player_close-up_drums": "set",
    "tabla_drums_top-down_view_-snare": "set",
    "tabla_hands_playing_up_close": "set",
    "tabla_performance_indian_concert": "set",
    "tabla_player_on_stage": "set",
    "tabla_practice_session": "set",
    "play_tabla_instrument": "set"
}

def remove_duplicates(image_files):
    hashes = set()
    unique = []
    for file in image_files:
        try:
            img = cv2.imread(file, cv2.IMREAD_COLOR)
            img_hash = hash(img.tobytes())
            if img_hash not in hashes:
                hashes.add(img_hash)
                unique.append(file)
        except:
            continue
    return unique

def super_resolve(img):
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(MODEL_PATH)
    sr.setModel("espcn", 2)
    return sr.upsample(img)

def apply_augmentations(img):
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    if random.random() > 0.5:
        pil = ImageEnhance.Brightness(pil).enhance(random.uniform(0.9, 1.1))
    if random.random() > 0.5:
        pil = ImageEnhance.Contrast(pil).enhance(random.uniform(0.9, 1.1))
    if random.random() > 0.5:
        pil = ImageEnhance.Color(pil).enhance(random.uniform(0.9, 1.1))
    img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

    augmentations = [img]
    augmentations.append(np.fliplr(img))
    augmentations.append(np.flipud(img))
    augmentations.append(np.rot90(img))
    augmentations.append(np.rot90(img, k=2))
    augmentations.append(np.rot90(img, k=3))

    return augmentations

def preprocess_image(img_path):
    img = cv2.imread(img_path)
    if img is None:
        return []

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (256, 256))
    img = cv2.bilateralFilter(img, 9, 75, 75)
    return apply_augmentations(super_resolve(img))

def process_all():
    df = pd.read_csv(METADATA_PATH)
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    for _, row in tqdm(df.iterrows(), total=len(df)):
        subdir = row["Search Term"].strip().lower().replace(" ", "_")
        file_name = os.path.basename(row["Image Path"])
        input_path = os.path.join(INPUT_ROOT, subdir, file_name)
        canonical = LABEL_MAP.get(subdir, None)

        if canonical is None or not os.path.exists(input_path):
            continue

        output_dir = os.path.join(OUTPUT_ROOT, canonical)
        os.makedirs(output_dir, exist_ok=True)

        for i, aug in enumerate(preprocess_image(input_path)):
            save_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_aug{i}.jpg")
            cv2.imwrite(save_path, cv2.cvtColor(aug, cv2.COLOR_RGB2BGR))

if __name__ == "__main__":
    process_all()
