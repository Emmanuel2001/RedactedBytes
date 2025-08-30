
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white) ![Uvicorn](https://img.shields.io/badge/Uvicorn-4B8BBE?style=flat&logo=python&logoColor=white) ![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat&logo=opencv&logoColor=white) ![Ultralytics](https://img.shields.io/badge/Ultralytics-YOLOv8-FF6F00?style=flat&logo=github&logoColor=white) ![PaddleOCR](https://img.shields.io/badge/PaddleOCR-005BAC?style=flat&logo=paddlepaddle&logoColor=white)

# 🔒 RedactedBytes

## ❓ The Problem  
Have you ever snapped a photo and later realized it contained more than you intended?

A selfie with a stranger in the background, a QR code stuck on the wall, or even a credit card peeking out of a wallet. These can all expose **Personally Identifiable Information (PII)**.  

At first glance, they may seem harmless. But PII allows malicious actors to **trace, profile, or even impersonate you**:  
- 🪪 A name tag can lead to a LinkedIn profile  
- 📱 A QR code can reveal a private link  
- 💳 A credit card number can expose financial accounts  

With AI models now capable of reading and correlating these shards of information instantly, the risks are multifold.  

**Our mission:** flip the script. Instead of leaving your data exposed, RedactedBytes **automatically detects and censors sensitive information**: faces, license plates, documents, names, and more before you share your images.  

## ✨ Features  

- 🕵️ *Automatic Detection of Sensitive Information*
  - Detects and censors faces, license plates, QR codes, and other identifiable objects
- 📄*Smart Document Protection*
  - Extracts text from images and flags sensitive data (names, IDs, credit card numbers, addresses)  
  - Automatically blurs or masks sensitive information without manual intervention  
- 🖱️*User-Friendly Interface*
  - Simple upload workflow: just click, upload, and get safe-to-share photos instantly  
  - Clean, intuitive design—no technical expertise required  
- 🤖 *AI-Powered Accuracy*
  - Leverages machine learning for robust object detection and text recognition  
  - Continuously improves with training data and refined detection logic  
- 🔐 *Privacy by Default*
  - Local processing options ensure sensitive data stays secure  
  - Outputs safe images without exposing private details  

## ⚡ Quick Start  

Get started with RedactedBytes in just a few steps!  

### Prerequisites  
- 🐳 [Docker](https://www.docker.com/) installed 

### Using Docker  
```bash
# Build the Docker image
docker build -t redactedbytes .

# Run the container
docker run -it --rm -p 8000:8000 redactedbytes
```
## 🛠️ Tech Stack  

**🌐 Frontend**  
- ⚛️ [React (Next.js)](https://nextjs.org/) → seamless media upload, real-time preview, and secure downloads  

**⚡ Backend**  
- 🚀 [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) → lightweight, high-performance API server  

**🧠 Computer Vision & AI**  
- 🖼️ [OpenCV](https://opencv.org/) → image processing & manipulation  
- 🎯 [Ultralytics](https://github.com/ultralytics/ultralytics) → object detection (faces, license plates, etc.)  
- 🔎 [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) → text extraction from documents  
- 📷 [ZXing-CPP](https://github.com/zxing-cpp/zxing-cpp) → barcode & QR code recognition  

## 🎥 Video Demo  
👉 *Coming soon… stay tuned!*  

## 📚 Datasets  
- [📑 COCO Pose Dataset (Ultralytics)](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco-pose.yaml)

# Citations

- *Wang, A., Liu, L., Chen, H., Lin, Z., Han, J., & Ding, G.* (2025). **YOLOE: Real-Time Seeing Anything.** arXiv [Cs.CV]. [![DOI:10.48550/arXiv.2503.07465](https://zenodo.org/badge/DOI/10.48550/arXiv.2503.07465.svg)](https://doi.org/10.48550/arXiv.2503.07465)
