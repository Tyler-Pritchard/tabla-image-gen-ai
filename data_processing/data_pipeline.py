import os
import cv2
import numpy as np
import random
from PIL import Image, ImageEnhance
from tqdm import tqdm

# Paths
INPUT_DIR = "data_collection/scraper/images"
OUTPUT_DIR = "data_processing/processed_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ESPCN_x2.pb')

def remove_duplicates(image_files):
    """Removes duplicate images based on hash comparison."""
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
    """Applies super-resolution using ESPCN model."""
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(MODEL_PATH)
    sr.setModel('espcn', 2)
    return sr.upsample(img)

def apply_color_jitter(img):
    """Randomly adjusts brightness, contrast, and saturation."""
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    if random.random() > 0.5:
        enhancer = ImageEnhance.Brightness(pil_img)
        pil_img = enhancer.enhance(random.uniform(0.8, 1.2))  # Slightly reduced range
    if random.random() > 0.5:
        enhancer = ImageEnhance.Contrast(pil_img)
        pil_img = enhancer.enhance(random.uniform(0.8, 1.2))
    if random.random() > 0.5:
        enhancer = ImageEnhance.Color(pil_img)
        pil_img = enhancer.enhance(random.uniform(0.8, 1.2))
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def add_gaussian_noise(img, mean=0, std=10):
    """Applies adaptive Gaussian noise with lower intensity."""
    noise = np.random.normal(mean, std, img.shape).astype(np.uint8)
    return cv2.addWeighted(img, 0.9, noise, 0.1, 0)  # Reduces noise impact

def random_crop(img, crop_size=(224, 224)):
    """Performs a random crop within the image."""
    h, w, _ = img.shape
    crop_h, crop_w = crop_size
    if h > crop_h and w > crop_w:
        y = random.randint(0, h - crop_h)
        x = random.randint(0, w - crop_w)
        return img[y:y+crop_h, x:x+crop_w]
    return img  # Return original if too small

def preprocess_and_augment_image(image_path, output_folder, image_size=(256, 256)):
    """Processes and augments images, applying noise before super-resolution."""
    try:
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            return

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, image_size, interpolation=cv2.INTER_LANCZOS4)
        img = cv2.bilateralFilter(img, 9, 75, 75)  # Noise reduction

        # Apply augmentations BEFORE super-resolution
        if random.random() > 0.5:
            img = apply_color_jitter(img)
        if random.random() > 0.5:
            img = add_gaussian_noise(img)  # Less aggressive noise
        if random.random() > 0.5:
            img = random_crop(img, crop_size=(224, 224))

        img = super_resolve_image(img)  # Apply super-resolution last

        # Augmentations
        augmented_images = [img]
        augmented_images.append(np.fliplr(img))  # Flip horizontally
        augmented_images.append(np.flipud(img))  # Flip vertically
        augmented_images.append(np.rot90(img))  # 90-degree rotation
        augmented_images.append(np.rot90(img, k=2))  # 180-degree rotation
        augmented_images.append(np.rot90(img, k=3))  # 270-degree rotation

        # Save augmented images
        for i, aug_img in enumerate(augmented_images):
            output_path = os.path.join(output_folder, f"aug_{i}_" + os.path.basename(image_path))
            cv2.imwrite(output_path, cv2.cvtColor(aug_img, cv2.COLOR_RGB2BGR))

    except Exception as e:
        print(f"Failed to process {image_path}: {e}")

def preprocess_images(input_dir, output_dir):
    """Processes the dataset, applies augmentations, and saves results."""
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
