# BlindNav AI – Intelligent Navigation Assistant

## Project overview
BlindNav AI is an MSc-level prototype for assisting blind and visually impaired users with intelligent scene understanding, risk alerts, route navigation, and emergency assistance. The system uses a Flask backend with a mobile-ready browser interface and works offline as much as possible through local inference and local map data.

## System architecture
- **Flask API Layer (`app.py`)**: Exposes `/detect`, `/risk`, `/route`, and `/emergency` endpoints.
- **AI Layer (`ai/`)**: YOLOv8 detection, nearest-center object tracking, and monocular distance estimation.
- **Navigation Layer (`navigation/`)**: OSM JSON parsing, graph build, and A* routing.
- **Risk Layer (`risk/`)**: Risk scoring and anti-spam alert manager.
- **Voice Layer (`voice/`)**: Offline speech synthesis via `pyttsx3`.
- **Sensors Layer (`sensors/`)**: Motion and fall detection utilities (feature approved = false by current policy).
- **Emergency Layer (`emergency/`)**: Emergency trigger with location capture and optional SMS workflow hook.

## Installation guide
Clone repository
```bash
git clone https://github.com/yourrepo/blindnav-ai
cd blindnav-ai
```

Create virtual environment
```bash
python -m venv venv
```

Activate environment
Linux / Mac
```bash
source venv/bin/activate
```

Windows
```bash
venv\Scripts\activate
```

Install dependencies
```bash
pip install -r requirements.txt
```

Download YOLO model
```bash
pip install ultralytics
yolo export model=yolov8n.pt format=torchscript
```

Move model to
```text
models/yolov8n.pt
```

## Running the application
```bash
python app.py
```

Open browser
```text
http://localhost:5000
```

## Testing object detection
1. Open the main page from mobile/desktop browser.
2. Tap **Start Detection** and grant camera permission.
3. Observe returned detections and risk levels in the JSON panel.

## Emergency testing
1. Click **Activate Emergency Mode**.
2. Approve geolocation request in browser.
3. Confirm spoken alert and displayed coordinates.
4. If SMS integration is configured in production, verify recipient receives alert.

## Run system test
```bash
python test_system.py
```

## Troubleshooting
- **Model load failure**: ensure `models/yolov8n.pt` exists and matches Ultralytics-compatible format.
- **No camera feed**: verify HTTPS/mobile browser permissions or localhost camera permission.
- **No speech output**: install system TTS drivers required by `pyttsx3`.
- **Route errors**: confirm `data/osm_map.json` nodes/edges are valid and connected.

## Future improvements
- Integrate robust OCR and semantic segmentation.
- Add real SMS provider integration (Twilio/telecom gateway).
- Enhance motion-based fall detection with temporal ML models.
- Add PWA packaging for better offline reliability.
- Improve turn instruction generation using bearing-based left/right inference.
