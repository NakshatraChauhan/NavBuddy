import { setupCamera, captureBase64 } from './camera.js';
import { VoiceAssistant } from './voice.js';

const ui = {
  statusText: document.getElementById('statusText'),
  statusRing: document.getElementById('statusRing'),
  gpsState: document.getElementById('gpsState'),
  visionState: document.getElementById('visionState'),
  micState: document.getElementById('micState'),
  audioState: document.getElementById('audioState'),
  guidance: document.getElementById('guidanceText'),
  objects: document.getElementById('objectsList'),
  metrics: document.getElementById('metricsText'),
  logs: document.getElementById('log'),
  video: document.getElementById('camera'),
  canvas: document.getElementById('snapshot'),
};

let running = false;
let timer = null;
let latestNav = '';

const log = (msg) => {
  const row = document.createElement('div');
  row.textContent = `${new Date().toLocaleTimeString()} - ${msg}`;
  ui.logs.prepend(row);
};

const voice = new VoiceAssistant(handleVoiceCommand, log);

function setState(active) {
  running = active;
  ui.statusText.textContent = active ? 'NAVIGATING' : 'STOPPED';
  ui.statusRing.classList.toggle('active', active);
  ui.visionState.textContent = active ? 'On' : 'Off';
  ui.visionState.classList.toggle('ok', active);
}

async function requestRuntimePermissions() {
  try {
    await new Promise((resolve) => {
      const u = new SpeechSynthesisUtterance('Audio enabled');
      u.onend = resolve;
      speechSynthesis.speak(u);
    });
    ui.audioState.textContent = 'On';
    ui.audioState.classList.add('ok');
  } catch {
    ui.audioState.textContent = 'Blocked';
  }

  const cam = await setupCamera(ui.video);
  if (cam.ok) {
    ui.micState.textContent = 'Active';
    ui.micState.classList.add('ok');
    ui.visionState.textContent = 'Ready';
    ui.visionState.classList.add('ok');
  } else {
    ui.micState.textContent = 'Denied';
    ui.visionState.textContent = 'Denied';
    log(`Camera/mic error: ${cam.error}`);
  }

  try {
    await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 6000,
      });
    });
    ui.gpsState.textContent = 'Locked';
    ui.gpsState.classList.add('ok');
  } catch {
    ui.gpsState.textContent = 'Denied';
  }
}

async function detectOnce() {
  if (!running) return;
  const frame = captureBase64(ui.video, ui.canvas);

  try {
    const res = await fetch('/detect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ frame }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    ui.guidance.textContent = data.navigation.message;
    ui.objects.innerHTML = '';
    data.objects.slice(0, 5).forEach((o) => {
      const li = document.createElement('li');
      li.textContent = `${o.label} | ${o.direction} | ${o.distance_m}m (${o.distance_band})`;
      ui.objects.appendChild(li);
    });

    const m = data.metrics;
    ui.metrics.textContent = `FPS: ${m.avg_fps} | Latency: ${m.avg_latency_ms}ms | Detector: ${m.detector_mode} | Depth: ${m.depth_mode}`;

    if (data.navigation.speak && data.navigation.message !== latestNav) {
      voice.speak(data.navigation.message, true);
      latestNav = data.navigation.message;
    }
  } catch (err) {
    log(`Network/detection error: ${err.message}`);
  }
}

function startNavigation() {
  if (running) return;
  setState(true);
  timer = setInterval(detectOnce, 200);
  voice.speak('Navigation started. Scanning surroundings now.', true);
}

function stopNavigation() {
  setState(false);
  if (timer) clearInterval(timer);
  timer = null;
  voice.speak('Navigation stopped.', true);
}

async function handleVoiceCommand(command) {
  if (command.includes('start navigation')) {
    startNavigation();
  } else if (command.includes('stop navigation')) {
    stopNavigation();
  } else if (command.includes('describe surroundings') || command.includes('what is in front of me')) {
    const res = await fetch('/describe_scene');
    const data = await res.json();
    voice.speak(data.summary, true);
  } else {
    voice.speak('Say start navigation, stop navigation, or describe surroundings.');
  }
}

(async function init() {
  await requestRuntimePermissions();
  voice.start();
  setState(false);
  ui.guidance.textContent = 'Assistant ready. Say Start navigation.';
})();
