import os
import shutil
import cv2
import csv
from tqdm import tqdm

# Directories
PROCESSED_IMAGES_DIR = "data_processing/processed_images"
TRAINING_IMAGES_DIR = "data_training/images"
METADATA_FILE = "data_training/metadata.csv"

# Ensure training directory exists
os.makedirs(TRAINING_IMAGES_DIR, exist_ok=True)

def resize_image(image_path, size=(512, 512)):
    """Resize image to a fixed size."""
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        print(f"❌ Failed to read image: {image_path}")
        return None
    img = cv2.resize(img, size, interpolation=cv2.INTER_LANCZOS4)
    return img

def prepare_dataset():
    """Move images into a single directory and resize them for training."""
    metadata = []
    image_count = 0
    
    for folder in os.listdir(PROCESSED_IMAGES_DIR):
        folder_path = os.path.join(PROCESSED_IMAGES_DIR, folder)
        if os.path.isdir(folder_path):
            for file in tqdm(os.listdir(folder_path), desc=f"Processing {folder}"):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    img = resize_image(file_path)
                    if img is not None:
                        new_filename = f"tabla_{image_count:04d}.jpg"
                        new_path = os.path.join(TRAINING_IMAGES_DIR, new_filename)
                        cv2.imwrite(new_path, img)
                        metadata.append([new_filename, folder, os.path.abspath(new_path)])
                        image_count += 1
    
    # Save metadata
    with open(METADATA_FILE, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filename", "canonical_label", "file_path"])
        writer.writerows(metadata)
    
    print(f"✅ Dataset preparation complete. {image_count} images ready for training.")

if __name__ == "__main__":
    prepare_dataset()
