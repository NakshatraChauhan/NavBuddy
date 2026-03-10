export async function setupCamera(videoEl) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: true });
    videoEl.srcObject = stream;
    await videoEl.play();
    return { ok: true, stream };
  } catch (err) {
    return { ok: false, error: err?.message || 'Camera permission denied' };
  }
}

export function captureBase64(videoEl, canvasEl) {
  const ctx = canvasEl.getContext('2d');
  ctx.drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height);
  return canvasEl.toDataURL('image/jpeg', 0.72);
}
