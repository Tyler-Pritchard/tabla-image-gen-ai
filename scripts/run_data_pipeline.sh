#!/bin/bash

echo "🧹 Cleaning old processed images..."
rm -rf data_processing/processed_images

echo "🚀 Running image processing pipeline..."
python data_processing/data_pipeline.py

echo "🧾 Generating metadata.csv..."
python data_processing/dataset_prep.py

echo "✅ All steps complete. Processed images and metadata are ready."
