const BASE_URL = "http://localhost:8000";

export async function fetchPosts(limit = 10, offset = 0) {
  const res = await fetch(`${BASE_URL}/api/posts?limit=${limit}&offset=${offset}`);
  return res.json();
}

export async function fetchDistribution(hours = 24) {
  const res = await fetch(`${BASE_URL}/api/sentiment/distribution?hours=${hours}`);
  return res.json();
}

export async function fetchAggregateData(period) {
  const res = await fetch(`${BASE_URL}/api/sentiment/aggregate?period=${period}`);
  return res.json();
}

export function connectWebSocket(onMessage, onError, onClose) {
  const ws = new WebSocket("ws://localhost:8000/ws/sentiment");
  ws.onmessage = (e) => onMessage(JSON.parse(e.data));
  ws.onerror = onError;
  ws.onclose = onClose;
  return ws;
}
