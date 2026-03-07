# Blind Navigation Assistant

A simple, stable, voice-first assistive navigation system for visually impaired users, built with **Python + Flask**.

## Initial Analysis (What was broken and fixed)

### What was broken
- Missing explicit hardware permission handling for camera, microphone, speaker, and GPS.
- Voice commands were vulnerable to minor phrase variations and microphone failures.
- Navigation needed stronger real-world safety behavior (short alerts + anti-spam cooldown + predictable status).
- Startup lacked environment-driven configuration and production-focused deployment guidance.
- No automated tests for critical system behaviors.

### What was fixed
- Added a mandatory permission flow before hardware usage.
- Hardened voice command routing and microphone failure handling.
- Improved navigation safety loop with cooldown and concise alerts.
- Added environment-configurable startup and Gunicorn deployment support.
- Added `tests/test_system.py` for permissions, model load, voice commands, and navigation pipeline checks.

---

## Architecture

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
  permissions/
    permission_manager.py
  utils/
    logger.py
  templates/
    index.html
  models/
    yolov8n.pt
  tests/
    test_system.py
  requirements.txt
  README.md
```

---

## Core Features

1. Scene Description (`describe scene`)
2. Obstacle Detection
3. Navigation Mode (`start navigation` / `stop navigation`)
4. Voice Command Control
5. Help Command (`help`)
6. Status Command (`status`)

All actions return spoken feedback when speaker permission is granted.

---

## Voice Commands

- `start navigation`
- `stop navigation`
- `describe scene`
- `stop scan`
- `status`
- `help`

### Help response
The system says exactly:

> "Available commands are: start navigation, stop navigation, describe scene, stop scan, status, help."

Commands are also listed in the web UI.

---

## Mandatory Permission System

At startup, the app asks permissions for:
- Camera
- Microphone
- GPS location
- Audio speaker

If denied, dependent features are safely disabled.

Environment override options:
- `BLINDNAV_AUTO_APPROVE=true`
- `BLINDNAV_PERMISSION_CAMERA=yes|no`
- `BLINDNAV_PERMISSION_MICROPHONE=yes|no`
- `BLINDNAV_PERMISSION_GPS=yes|no`
- `BLINDNAV_PERMISSION_SPEAKER=yes|no`

---

## Installation

### Create environment
```bash
python -m venv venv
```

### Activate environment
Linux / Mac:
```bash
source venv/bin/activate
```

Windows:
```bash
venv\Scripts\activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Install YOLO
```bash
pip install ultralytics
```

### Model placement
Put your model at:
```text
models/yolov8n.pt
```

---

## Running Locally

```bash
python app.py
```

Open:
```text
http://localhost:5000
```

---

## Production Deployment

```bash
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

Optional environment variables:
- `BLINDNAV_MODEL_PATH=models/yolov8n.pt`
- `BLINDNAV_TARGET_FPS=4`
- `BLINDNAV_HOST=0.0.0.0`
- `BLINDNAV_PORT=5000`
- `BLINDNAV_LOG_LEVEL=INFO`
- `BLINDNAV_LOG_DIR=logs`

---

## Hardware Requirements

- Camera (USB/internal)
- Microphone
- Speaker/audio output
- CPU-capable machine (no GPU required)

---

## Troubleshooting

### Camera not available
- Check camera permissions.
- Ensure no other app is locking the device.
- Review logs in `logs/blindnav.log`.

### Microphone not available
- Check microphone permissions and selected input device.
- Voice control is disabled safely; web command buttons remain available.

### Speaker denied/unavailable
- Spoken feedback is muted intentionally.
- Use the web UI output and logs.

### Model loading failure
- Confirm `models/yolov8n.pt` exists and is compatible.
- Check stack traces in `logs/blindnav.log`.

### SpeechRecognition request issues
- `recognize_google` requires network access.
- Use web UI commands if offline.

---

## Testing

Run automated checks:

```bash
python -m unittest tests/test_system.py -v
```

Tests include:
- Permission manager behavior
- YOLO model loading path (mocked)
- Voice command handling
- Navigation scene/alert pipeline behavior
