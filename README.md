# Vision Companion (Blind Navigation Assistant)

This project is a browser-based blind navigation assistant with a Flask backend and HTML/JavaScript frontend.

It provides:
- Voice-first control (`Start navigation`, `Stop navigation`, `Describe surroundings`, `Where am I`, etc.)
- Camera frame processing for obstacle detection
- Distance + direction estimation
- Spoken safety guidance
- GPS reverse location lookup

---

## 1) Project Structure

```text
/workspace/NavBuddy
├── README.md
└── blind_nav_app
    ├── app.py
    ├── object_detection.py
    ├── navigation_logic.py
    ├── scene_description.py
    ├── gps_module.py
    ├── templates
    │   └── index.html
    └── static
        ├── voice.js
        ├── camera.js
        ├── navigation.js
        └── permissions.js
```

---

## 2) Prerequisites

Install the following on your machine:
- Python 3.10+ (recommended: 3.11 or 3.12)
- A modern browser (Chrome/Edge recommended for Web Speech API)
- Webcam and microphone
- Internet connection (optional but recommended for GPS reverse geocoding and YOLO model download)

---

## 3) Create Virtual Environment

From repo root:

```bash
python -m venv .venv
```

Activate:

### Linux/macOS
```bash
source .venv/bin/activate
```

### Windows (PowerShell)
```powershell
.venv\Scripts\Activate.ps1
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

---

## 4) Install Dependencies

Install required runtime packages:

```bash
pip install flask requests pillow numpy opencv-python-headless
```

### Optional (for YOLO object detection)

If you want full YOLO detection instead of fallback contour detection:

```bash
pip install ultralytics
```

> Note: first YOLO run may download model weights (`yolov8n.pt`).

---

## 5) Quick Sanity Check

Run Python syntax check:

```bash
python -m py_compile blind_nav_app/*.py
```

---

## 6) Run the Application

Start Flask server:

```bash
cd blind_nav_app
python app.py
```

Server should start at:

```text
http://localhost:5000
```

Open this URL in browser.

---

## 7) Browser Permissions (Must Allow)

On first page load, allow these permissions:
1. Camera
2. Microphone
3. Location (GPS)
4. Audio playback

The UI status cards update based on granted/denied state.

---

## 8) Voice Commands

Say commands clearly in English:

- "Start navigation"
- "Stop navigation"
- "Describe surroundings"
- "What is in front of me"
- "Where am I"
- "Guide me forward"

Behavior:
- Voice recognition runs continuously.
- Spoken responses are generated with Speech Synthesis.
- During navigation, camera frames are sent to Flask for obstacle analysis.

---

## 9) API Endpoints (Backend)

### `GET /`
Serves UI page.

### `POST /detect_objects`
Body:
```json
{ "frame": "data:image/jpeg;base64,..." }
```
Returns detections and guidance.

### `GET /describe_scene`
Returns scene summary based on latest detections.

### `POST /gps_location`
Body:
```json
{ "latitude": 40.7, "longitude": -73.9 }
```
Returns human-readable nearby location.

### `POST /process_voice`
Body:
```json
{ "command": "start navigation" }
```
Returns recognized command response.

---

## 10) How Detection Works

1. Browser captures camera frames.
2. Frames are posted to `/detect_objects`.
3. Backend attempts YOLO inference (if `ultralytics` exists).
4. If YOLO is unavailable, fallback heuristic obstacle detection is used.
5. Distance is approximated from bounding box width.
6. Direction is classified as Left / Center / Right.
7. Navigation logic picks nearest obstacle and emits calm guidance.

---

## 11) Troubleshooting

### A) `ModuleNotFoundError: No module named 'flask'`
Install dependencies again in activated virtual environment:

```bash
pip install flask requests pillow numpy opencv-python-headless
```

### B) Voice recognition not working
- Use Chrome/Edge.
- Ensure microphone permission is granted.
- Ensure browser supports `SpeechRecognition` / `webkitSpeechRecognition`.

### C) GPS says unavailable
- Allow Location permission in browser.
- Check OS location services are enabled.
- Use HTTPS or localhost (localhost is supported for geolocation in modern browsers).

### D) YOLO not running
- Install optional dependency:
  ```bash
  pip install ultralytics
  ```
- Ensure internet on first run so model can be downloaded.

### E) No spoken output
- Ensure browser tab is not muted.
- Interact with page once if autoplay policy blocks initial speech.

---

## 12) Stop Application

In terminal running Flask:

```bash
Ctrl + C
```

Deactivate environment when done:

```bash
deactivate
```

---

## 13) Recommended Real-World Usage Notes

- Keep camera pointed forward at chest/head height.
- Walk slowly; rely on repeated guidance.
- Use earphones in one ear for safer outdoor awareness.
- Treat this as assistive software, not a medical-grade safety guarantee.
