# Blind Navigation Assistant

A simple, stable, voice-first assistive navigation system for visually impaired users, built with **Python + Flask**.

The application provides:
- Scene description
- Obstacle-aware navigation alerts
- Voice command control
- Help and status responses

---

## 1) Project Overview

Blind Navigation Assistant uses a camera feed, YOLOv8 Nano object detection, and text-to-speech to help users understand their environment.

The design is intentionally minimal:
- CPU-friendly processing
- Clear short voice alerts
- Cooldown to avoid repeated alert spam
- Commands accessible by voice and web UI fallback

---

## 2) Architecture

```text
blindnav/
  app.py
  ai/
    detector.py
    scene_analyzer.py
  voice/
    speech_engine.py
    voice_controller.py
  navigation/
    navigator.py
  utils/
    logger.py
  templates/
    index.html
  models/
    yolov8n.pt
  requirements.txt
  README.md
```

### Module Responsibilities

- `app.py`: Flask app, startup wiring, API routes.
- `ai/detector.py`: YOLOv8n loading and detection filtering.
- `ai/scene_analyzer.py`: Converts detections into short scene descriptions and navigation alerts.
- `voice/speech_engine.py`: TTS engine wrapper (`pyttsx3`).
- `voice/voice_controller.py`: Continuous command listener (`SpeechRecognition`) and command routing.
- `navigation/navigator.py`: Camera lifecycle, navigation loop, cooldown logic, status/help handling.
- `utils/logger.py`: File + console logging setup.
- `templates/index.html`: Accessibility-friendly status and command listing UI.

---

## 3) Installation

### Create environment
```bash
python -m venv venv
```

### Activate environment
Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Install YOLO
```bash
pip install ultralytics
```

### Download model
```bash
yolo export model=yolov8n.pt format=torchscript
```

Place model in:
```text
models/yolov8n.pt
```

---

## 4) Run Application

```bash
python app.py
```

Open interface:
```text
http://localhost:5000
```

---

## 5) Voice Commands

Supported commands:
- `start navigation`
- `stop navigation`
- `describe scene`
- `stop scan`
- `status`
- `help`

### Help response
When user says `help`, system says:

> "Available commands are: start navigation, stop navigation, describe scene, stop scan, status, help."

The same commands are shown on the web interface.

---

## 6) Runtime Workflow

1. App starts and loads YOLO model.
2. Speech engine initializes.
3. Voice listener starts in background.
4. User gives voice commands.
5. Navigator executes action with spoken feedback.

Examples:
- `describe scene` → capture frame, run detection, speak short summary.
- `start navigation` → continuous scan + cooldown alerts (e.g., “Obstacle ahead”, “Path clear”).
- `status` → spoken current system state.

---

## 7) Troubleshooting

### Camera failure
- Ensure no other app is locking the camera.
- Confirm system camera permissions for Python.
- Check logs at `logs/blindnav.log`.

### Microphone failure
- Confirm microphone permissions.
- Ensure input device is connected and default.
- If unavailable, app still supports manual web command triggers.

### Model loading error
- Confirm `models/yolov8n.pt` exists.
- Verify version compatibility (`ultralytics` from requirements).
- Review `logs/blindnav.log` for stack trace.

### Voice recognition request errors
- `recognize_google` requires network access.
- If offline, use the web command buttons as fallback.

---

## 8) Performance Notes

- Runs on CPU.
- Uses resized frames for efficient YOLO inference.
- Navigation scan loop is throttled for practical CPU usage.
- Alert cooldown prevents repeated speech spam.
