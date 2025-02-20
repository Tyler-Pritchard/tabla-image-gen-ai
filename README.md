# **Tabla Drum Image Generator** 🎵🎨  

### **A Machine Learning Approach to Realistic Tabla Drum Image Generation**  

This project showcases **AI/ML expertise** through the development of a **custom-trained image generation model** focused on Indian **tabla drums**. By leveraging **diffusion models** and **GAN architectures**, the goal is to **correct inaccuracies in existing AI-generated tabla drum images** and produce **high-quality, culturally accurate representations**.

---

## **🚀 Project Goals**
- **Curate & preprocess** a high-quality dataset of tabla drum images.
- **Train** a **custom fine-tuned model** using **Stable Diffusion** and **GAN architectures**.
- **Evaluate & optimize** image fidelity using **FID and perceptual loss metrics**.
- **Deploy** the model via **a web-based API** with a front-end for image generation.

---

## **🛠 Tools & Technologies**
### **Machine Learning & AI**
- **Frameworks**: PyTorch, TensorFlow
- **Model Architectures**: Stable Diffusion, DreamBooth, StyleGAN, GAN-based approaches
- **Data Augmentation**: OpenCV, Albumentations

### **Data Collection & Processing**
- **Web Scraping**: Selenium, Playwright, Requests
- **Annotation**: Label Studio
- **Storage**: Cloud-based dataset hosting (AWS S3, Hugging Face Datasets)

### **Deployment & Serving**
- **API Hosting**: FastAPI, Flask
- **Web UI**: Streamlit, Gradio, Hugging Face Spaces
- **Infrastructure**: Docker, Kubernetes (planned for production-scale deployment)

### **Project Management & Version Control**
- **GitHub Actions**: CI/CD automation for training jobs & model updates
- **Experiment Tracking**: Weights & Biases (planned integration)
- **Collaboration Tools**: Notion, Trello

---

## **📂 Project Structure**
```
tabla-image-gen-ai/
│── data_collection/        # Web scraping & dataset collection
│   ├── scraper/            # Selenium/Playwright-based image scraper
│   ├── images/             # Raw and processed dataset images
│   ├── metadata/           # Image metadata & annotations
│
│── data_processing/        # Dataset cleaning & augmentation pipeline
│   ├── preprocessing.py    # Image resizing, enhancement, noise reduction
│   ├── augmentation.py     # Data augmentation transformations
│
│── model_training/         # ML model training pipeline
│   ├── train.py            # Fine-tunes diffusion model or GAN on dataset
│   ├── evaluation.py       # Calculates FID, PSNR, SSIM
│
│── deployment/             # Web-based model serving
│   ├── api/                # FastAPI/Flask server for generating images
│   ├── ui/                 # Streamlit/Gradio front-end
│
│── notebooks/              # Jupyter notebooks for data exploration
│── app/requirements.txt    # Python dependencies
│── README.md               # This document
```

---

## **⚡ Setup Instructions**
### **1️⃣ Clone this repository**
```bash
git clone https://github.com/tyler-pritchard/tabla-image-gen-ai.git
cd tabla-image-gen-ai
```

### **2️⃣ Install dependencies**
```bash
pip install -r app/requirements.txt
```

### **3️⃣ Run the web scraper (to collect tabla drum images)**
```bash
python data_collection/scraper/tabla_image_scraper.py
```

### **4️⃣ Preprocess the images for model training**
```bash
python data_processing/preprocessing.py
```

### **5️⃣ Train the AI model**
```bash
python model_training/train.py
```

### **6️⃣ Deploy the image generation model**
```bash
python deployment/api/main.py
```

---

## **📈 Current Progress**
✅ **Web scraping functional** (collecting 100+ high-res tabla images)  
✅ **Dataset preprocessing implemented** (image cleaning, augmentation)  
🚧 **Model fine-tuning in progress** (Stable Diffusion adaptation)  
🚧 **Deployment infrastructure in planning**  

---

## **👨‍💻 Why This Project Matters**
1. **Addresses a real-world AI failure**: Existing generative AI models struggle with **authentic tabla representations**.
2. **Demonstrates ML proficiency**: Covers **data collection → model training → deployment**.
3. **Production-ready deployment**: Architected for **real-world applications** with **Scalable APIs**.
4. **Extensible for other domains**: Can be adapted for **any niche image dataset**.

---

## **📩 Connect & Collaborate**
- **Author**: Tyler Pritchard  
- **GitHub**: [github.com/tyler-pritchard](https://github.com/tyler-pritchard)  
- **LinkedIn**: [linkedin.com/in/tyler-pritchard](https://linkedin.com/in/tyler-pritchard)  
