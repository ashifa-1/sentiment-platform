import axios from 'axios';

// IMPORTANT: Replace with your actual forwarded Codespace URL for port 8000
const API_BASE = "https://ominous-yodel-x55vp9pqp79wcp9qq-8000.app.github.dev/api"; 
const WS_BASE = "ws://localhost:8000/ws/sentiment";

export const apiService = {
  fetchPosts: (limit = 10) => axios.get(`${API_BASE}/posts?limit=${limit}`),
  fetchDistribution: (hours = 24) => axios.get(`${API_BASE}/sentiment/distribution?hours=${hours}`),
  fetchAggregateData: (period = 'minute') => axios.get(`${API_BASE}/sentiment/aggregate?period=${period}`),
  connectWebSocket: (onMessage) => {
    const ws = new WebSocket(WS_BASE);
    ws.onmessage = (event) => onMessage(JSON.parse(event.data));
    return ws;
  }
};