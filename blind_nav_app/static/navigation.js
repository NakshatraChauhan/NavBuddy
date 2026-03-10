import { requestPermissions } from './permissions.js';
import { VoiceController } from './voice.js';
import { attachCamera, captureFrame } from './camera.js';

const ui = {
  status: document.getElementById('status'),
  statusRing: document.getElementById('statusRing'),
  gpsState: document.getElementById('gpsState'),
  visionState: document.getElementById('visionState'),
  micState: document.getElementById('micState'),
  audioState: document.getElementById('audioState'),
  guidanceText: document.getElementById('guidanceText'),
  detectionsList: document.getElementById('detectionsList'),
  log: document.getElementById('log'),
  video: document.getElementById('camera'),
  canvas: document.getElementById('snapshot'),
};

let navigationEnabled = false;
let detectorTimer = null;
let lastSpokenGuidance = '';
let latestGps = null;

const setMode = (active) => {
  ui.status.textContent = active ? 'Navigating' : 'Stopped';
  ui.statusRing.classList.toggle('active', active);
  ui.visionState.textContent = active ? 'On' : 'Off';
  ui.visionState.classList.toggle('ok', active);
};

const log = (text) => {
  const row = document.createElement('div');
  row.textContent = `${new Date().toLocaleTimeString()} - ${text}`;
  ui.log.prepend(row);
};

const voice = new VoiceController({
  onCommand: (cmd) => processVoiceCommand(cmd.toLowerCase()),
  log,
});

async function processVoiceCommand(command) {
  const known = [
    'start navigation',
    'stop navigation',
    'describe surroundings',
    'what is in front of me',
    'where am i',
    'guide me forward',
  ];

  const match = known.find((k) => command.includes(k));
  const active = match || command;

  await fetch('/process_voice', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command: active }),
  });

  if (active === 'start navigation') {
    startNavigation();
    voice.speak('Navigation started. I am scanning for obstacles.', true);
  } else if (active === 'stop navigation') {
    stopNavigation();
    voice.speak('Navigation stopped.', true);
  } else if (active === 'describe surroundings' || active === 'what is in front of me') {
    const res = await fetch('/describe_scene');
    const payload = await res.json();
    voice.speak(payload.summary, true);
  } else if (active === 'where am i') {
    if (latestGps) {
      const res = await fetch('/gps_location', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(latestGps),
      });
      const payload = await res.json();
      voice.speak(`You are near ${payload.location}.`, true);
    } else {
      voice.speak('Location not available yet.');
    }
  } else if (active === 'guide me forward') {
    if (!navigationEnabled) startNavigation();
    voice.speak('Guiding now. Keep phone camera facing forward.', true);
  } else {
    voice.speak('I heard you. Say start navigation, describe surroundings, or where am I.');
  }
}

async function detectLoop() {
  if (!navigationEnabled) return;

  const frame = captureFrame(ui.video, ui.canvas);
  const res = await fetch('/detect_objects', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ frame }),
  });

  if (!res.ok) return;
  const payload = await res.json();
  const { detections, guidance } = payload;

  ui.guidanceText.textContent = guidance.message;
  ui.detectionsList.innerHTML = '';
  detections.slice(0, 4).forEach((d) => {
    const li = document.createElement('li');
    li.textContent = `${d.label} - ${d.direction}, ${d.distance_m}m`;
    ui.detectionsList.appendChild(li);
  });

  if (guidance.warning && guidance.message !== lastSpokenGuidance) {
    voice.speak(guidance.message, true);
    lastSpokenGuidance = guidance.message;
  }
}

function startNavigation() {
  if (navigationEnabled) return;
  navigationEnabled = true;
  setMode(true);
  detectorTimer = setInterval(detectLoop, 600);
}

function stopNavigation() {
  navigationEnabled = false;
  if (detectorTimer) clearInterval(detectorTimer);
  detectorTimer = null;
  setMode(false);
}

(async function init() {
  ui.status.textContent = 'Requesting';
  const perms = await requestPermissions(ui);

  if (perms.stream) {
    attachCamera(ui.video, perms.stream);
  }

  if (perms.location) {
    latestGps = {
      latitude: perms.location.coords.latitude,
      longitude: perms.location.coords.longitude,
    };
  }

  voice.startListening();
  setMode(false);
  voice.speak('Assistant ready. Say start navigation when you are ready.');
})();
