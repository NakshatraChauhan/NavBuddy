# AI-Based Blind Navigation Assistance System (MSc-Level)

Real-time browser + Flask assistive navigation prototype using:
- **YOLOv8** for object detection
- **MiDaS** for depth estimation
- **Navigation engine** for movement decisions
- **Voice guidance** in browser (SpeechSynthesis)
- **Runtime permissions** for camera/microphone/GPS/audio

## Project layout

```text
blind_navigation_ai/
  app.py
  object_detection.py
  depth_estimation.py
  navigation_engine.py
  voice_feedback.py
  scene_analyzer.py
  models/
    yolov8n.pt   # optional local weights
  templates/
    index.html
  static/
    camera.js
    voice.js
    navigation.js
requirements.txt
```

## 1) Setup environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\Activate.ps1  # Windows PowerShell
python -m pip install --upgrade pip
```

## 2) Install dependencies

```bash
pip install -r requirements.txt
```

## 3) (Optional) Place YOLO weights locally

- Put `yolov8n.pt` in `blind_navigation_ai/models/`.
- If absent, ultralytics may auto-download when internet is available.

## 4) Run app

```bash
cd blind_navigation_ai
python app.py
```

Open browser at:

```text
http://localhost:5000
```

## 5) Runtime permission flow (automatic)

On load the app requests/activates:
1. Audio playback test
2. Camera + microphone via `getUserMedia()`
3. GPS via Geolocation API
4. Continuous speech recognition

## 6) Voice commands

- "Start navigation"
- "Stop navigation"
- "Describe surroundings"
- "What is in front of me"

## 7) Backend API

- `POST /detect` : frame -> YOLO + MiDaS + navigation + metrics
- `GET /navigation` : latest navigation advice
- `GET /describe_scene` : verbal scene summary

## 8) Performance / metrics

Each detection response includes:
- `avg_fps`
- `avg_latency_ms`
- `detection_accuracy_proxy`
- detector/depth mode (`yolov8`/`midas` vs fallback)

Metrics also print in server console as `[METRICS] ...`.

## 9) Notes

- Browser speech is used for low-latency feedback.
- `voice_feedback.py` provides optional server-side `pyttsx3` TTS helper.
- If torch/MiDaS/YOLO fail, the system falls back gracefully (heuristic detection/depth) so demo still runs.

## 10) Stop

Press `Ctrl + C` in terminal.
