# Installation

### Install GPU-accelerated PyTorch first (requires CUDA 12.1+ compatible driver)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

### Then install the rest
pip install -r requirements.txt

---

# Environment Setup

### Configure `.env` secrets
- [x] `OPEN_ROUTER_API_KEY=YOUR_OPEN_ROUTER_KEY`
- [x]  `HP_API_KEY=YOUR_HUGGING_FACE_SECRET`