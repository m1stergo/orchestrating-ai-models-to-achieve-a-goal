# Orchestrating AI Models to Streamline Product Descriptions and Media for E-commerce

This repository implements a modular platform for AI-assisted product listings (titles, descriptions, images, and audio).  
The system is divided into **backend**, **AI services**, and **frontend**, following a microservices architecture.

---

## Project Structure
```bash
.
├── backend/ # Core API (FastAPI + PostgreSQL)
├── services/ # AI microservices
│ ├── qwen-describe-image/ # Vision-Language model (image attribute extraction)
│ ├── mistral-generate-description/ # LLM for product description generation
│ └── chatterbox-text-to-speech/ # TTS (Text-to-Speech)
└── frontend/ # Web interface (Vue 3 + Vite + pnpm)
```
Each service has its own **README.md**, since they are designed for independent deployment.

---

## Backend

1. Create a virtual environment and install dependencies:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   .venv\Scripts\activate      # Windows
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Copy .env.example to .env and fill in the values
   cp .env.example .env
   
   # Create database tables
   python create_tables.py

   # Run the backend
   python main.py```

## AI Services

Each service (qwen, mistral, chatterbox) runs separately.

Enter the service folder:
```bash
cd services/qwen-describe-image
```

Install base dependencies:
```bash
pip install -r requirements.txt
```

Install PyTorch manually depending on your GPU and CUDA version
(do this after installing requirements to avoid conflicts):
```bash
# Example for CUDA 12.8 Blackwell (RTX 5090)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```
See more options in: [PyTorch Installation Guide](https://pytorch.org/get-started/locally/)

Copy .env.example to .env and fill in the values:
```bash
cp .env.example .env
```


## Frontend

Install dependencies:
```
cd frontend
npm install -g pnpm
pnpm install
```

Copy .env.example to .env and fill in the values:
```bash
cp .env.example .env
```

Start the development server:
```
pnpm dev
```