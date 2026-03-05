const video = document.getElementById('camera');
const canvas = document.getElementById('canvas');
const output = document.getElementById('detectionOutput');
const emergencyOutput = document.getElementById('emergencyOutput');
const assistToggle = document.getElementById('assistToggle');
const radarStatus = document.getElementById('radarStatus');
const visionState = document.getElementById('visionState');
let streamRef = null;
let timer = null;

async function startCamera() {
  streamRef = await navigator.mediaDevices.getUserMedia({
    video: { facingMode: 'environment' },
    audio: false
  });
  video.srcObject = streamRef;
  await video.play();
}

function stopCamera() {
  if (timer) clearInterval(timer);
  timer = null;
  if (streamRef) {
    streamRef.getTracks().forEach(t => t.stop());
  }
  streamRef = null;
  assistToggle.classList.remove('active');
  radarStatus.textContent = 'STOPPED';
  visionState.textContent = 'Off';
}

async function runDetection() {
  if (!streamRef) await startCamera();
  const ctx = canvas.getContext('2d');
  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;

  assistToggle.classList.add('active');
  radarStatus.textContent = 'ACTIVE';
  visionState.textContent = 'Scanning';

  timer = setInterval(async () => {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const image = canvas.toDataURL('image/jpeg', 0.7);

    const detectRes = await fetch('/detect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image })
    });
    const detectData = await detectRes.json();

    const riskRes = await fetch('/risk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ detections: detectData.detections || [] })
    });
    const riskData = await riskRes.json();

    (riskData.results || []).forEach(r => {
      if (r.risk_level === 'HIGH' && navigator.vibrate && r.vibration_pattern) {
        navigator.vibrate(r.vibration_pattern);
      }
    });

    output.textContent = JSON.stringify(riskData, null, 2);
  }, 200);
}

assistToggle.addEventListener('click', async () => {
  if (timer) {
    stopCamera();
    return;
  }

  try {
    await runDetection();
  } catch (error) {
    radarStatus.textContent = 'DENIED';
    visionState.textContent = 'Permission blocked';
    output.textContent = `Detection start failed: ${error}`;
    stopCamera();
  }
});

document.getElementById('emergencyBtn').addEventListener('click', async () => {
  let lat = 0;
  let lon = 0;

  if (navigator.geolocation) {
    await new Promise(resolve => {
      navigator.geolocation.getCurrentPosition(
        p => {
          lat = p.coords.latitude;
          lon = p.coords.longitude;
          resolve();
        },
        () => resolve(),
        { enableHighAccuracy: true, timeout: 5000 }
      );
    });
  }

  const response = await fetch('/emergency', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lat, lon, phone: '+10000000000' })
  });
  const data = await response.json();
  emergencyOutput.textContent = JSON.stringify(data, null, 2);
  if (navigator.vibrate) navigator.vibrate([250, 100, 250]);
});
