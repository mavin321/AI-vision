# Local AI Vision Keyboard

A fully local desktop/web hybrid that watches your webcam for hand gestures and maps them to key presses, shortcuts, or macros. FastAPI hosts the API/WebSocket, a Vite React UI gives live feedback, and an optional C++/pybind11 module accelerates frame preprocessing.

## Project Layout
```
backend/             FastAPI app + AI loop + keyboard control
frontend/            React (Vite) UI for preview + mapping editor
vision/              C++ acceleration layer (pybind11 + OpenCV)
models/hand_model.tflite  Placeholder lightweight model
```

## Prerequisites
- Python 3.10+
- Node.js 18+
- CMake 3.14+, a C++17 toolchain, OpenCV dev packages, and pybind11 (via pip or your package manager)
- Webcam attached to the machine

## Setup & Run
### Backend
```bash
cd backend
python -m venv .venv && source .AIenv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev   # served at http://localhost:5173
```

### C++ Acceleration (optional but recommended)
```bash
cd vision
sudo apt-get install pybind11-dev
sudo apt-get install libopencv-dev
cmake -S . -B build
cmake --build build
# Copy resulting vision.*.so/pyd into backend/.venv/lib/python.../site-packages or add build dir to PYTHONPATH
```

## Key Features
- **Hand gesture detection** via OpenCV + MediaPipe with optional TFLite model hook
- **WebSocket gesture feed** `/ws/gestures` for real-time UI updates
- **REST endpoints**
  - `GET/POST /api/gesture` read/toggle detection
  - `GET/POST /api/settings` manage gesture → key mappings (stored in `backend/mappings.json`)
  - `POST /api/keyboard/press` simulate a key action
- **Keyboard output** with `pynput` (fallback to `keyboard` lib)
- **C++ preprocessing** `vision.preprocess(frame)` for fast denoising/edges

## Architecture Overview
- **AI loop** (`backend/services/ai_loop.py`): pulls frames from `VisionService`, runs preprocessing + MediaPipe landmarks, emits predictions, executes mapped macros through `KeyboardService`, and broadcasts to WebSocket clients.
- **State & config**: mappings persisted to `backend/mappings.json`; defaults seeded on first run. Toggle detection via `/api/gesture`.
- **Frontend UI**: webcam preview, live gesture label, start/stop detection, and a mapping editor with inline "Try" to test macros.

## Extending
- Replace `models/hand_model.tflite` with your trained model and load it in `VisionService.extract_landmarks`.
- Add more robust gesture classifiers in `VisionService` and hook into the `AILoopService` mapping logic.
- Implement GPU/CUDA paths inside `vision.cpp` (e.g., using OpenCV CUDA filters) and expose via pybind11.
- Add sound feedback by triggering a small audio clip on new predictions in the frontend.

## Security & Privacy
Everything runs locally—no cloud calls. Webcam frames stay on-device.

## Troubleshooting
- If OpenCV/MediaPipe are missing, the service will log warnings and emit `unknown` gestures until dependencies are installed.
- Keyboard simulation may require accessibility permissions on macOS/Windows.
- Ensure the WebSocket URL matches your backend host/port when accessing from another device; set `VITE_API_URL` accordingly.
