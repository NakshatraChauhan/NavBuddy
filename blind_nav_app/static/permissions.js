function setText(el, text) {
  if (el) el.textContent = text;
}

function setCardState(el, text, ok = false) {
  if (!el) return;
  el.textContent = text;
  el.classList.toggle('ok', ok);
}

export async function requestPermissions(ui) {
  const result = {
    camera: false,
    microphone: false,
    gps: false,
    audio: false,
    stream: null,
    location: null,
  };

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    result.camera = true;
    result.microphone = true;
    result.stream = stream;
    setCardState(ui.visionState, 'Ready', true);
    setCardState(ui.micState, 'Active', true);
  } catch {
    setCardState(ui.visionState, 'Denied');
    setCardState(ui.micState, 'Denied');
  }

  try {
    result.location = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 6000,
      });
    });
    result.gps = true;
    setCardState(ui.gpsState, 'Locked', true);
  } catch {
    setCardState(ui.gpsState, 'Unavailable');
  }

  try {
    await new Promise((resolve) => {
      const utterance = new SpeechSynthesisUtterance('Audio enabled.');
      utterance.onend = resolve;
      speechSynthesis.speak(utterance);
    });
    result.audio = true;
    setCardState(ui.audioState, 'On', true);
  } catch {
    setCardState(ui.audioState, 'Blocked');
  }

  setText(ui.status, 'Stopped');
  return result;
}
