export function attachCamera(videoEl, stream) {
  videoEl.srcObject = stream;
}

export function captureFrame(videoEl, canvasEl) {
  const ctx = canvasEl.getContext('2d');
  ctx.drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height);
  return canvasEl.toDataURL('image/jpeg', 0.7);
}
