document.getElementById('routeBtn').addEventListener('click', async () => {
  const startLat = document.getElementById('startLat').value;
  const startLon = document.getElementById('startLon').value;
  const endLat = document.getElementById('endLat').value;
  const endLon = document.getElementById('endLon').value;

  const res = await fetch(`/route?start_lat=${startLat}&start_lon=${startLon}&end_lat=${endLat}&end_lon=${endLon}`);
  const data = await res.json();
  document.getElementById('routeOutput').textContent = JSON.stringify(data, null, 2);
});
