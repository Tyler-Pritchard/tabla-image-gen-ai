import os
import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm

INPUT_DIR = "data_collection/scraper/images"
OUTPUT_DIR = "data_processing/processed_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ESPCN_x2.pb')

def remove_duplicates(image_files):
    hashes = set()
    unique_files = []
    for file in image_files:
        try:
            img = cv2.imread(file, cv2.IMREAD_COLOR)
            img_hash = hash(img.tobytes())
            if img_hash not in hashes:
                hashes.add(img_hash)
                unique_files.append(file)
        except Exception as e:
            print(f"Error reading {file}: {e}")
    return unique_files

def super_resolve_image(img):
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(MODEL_PATH)
    sr.setModel('espcn', 2)
    return sr.upsample(img)

def preprocess_and_augment_image(image_path, output_folder, image_size=(256, 256)):
    try:
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, image_size, interpolation=cv2.INTER_LANCZOS4)
        img = cv2.bilateralFilter(img, 9, 75, 75)
        img = super_resolve_image(img)
        img_array = img / 255.0

        augmented_images = [img_array]
        augmented_images.append(np.fliplr(img_array))
        augmented_images.append(np.flipud(img_array))
        augmented_images.append(np.rot90(img_array))

        for i, aug_img in enumerate(augmented_images):
            output_path = os.path.join(output_folder, f"aug_{i}_" + os.path.basename(image_path))
            cv2.imwrite(output_path, cv2.cvtColor((aug_img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    except Exception as e:
        print(f"Failed to process {image_path}: {e}")

def preprocess_images(input_dir, output_dir):
    for folder in os.listdir(input_dir):
        folder_path = os.path.join(input_dir, folder)
        if os.path.isdir(folder_path):
            output_folder = os.path.join(output_dir, folder)
            os.makedirs(output_folder, exist_ok=True)

            image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            unique_files = remove_duplicates(image_files)

            for file_path in tqdm(unique_files, desc=f"Processing {folder}"):
                preprocess_and_augment_image(file_path, output_folder)

if __name__ == "__main__":
    preprocess_images(INPUT_DIR, OUTPUT_DIR)
