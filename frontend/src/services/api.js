const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

/* -------------------------------------------------
   1. Fetch Posts (pagination + filters)
-------------------------------------------------- */
export async function fetchPosts(limit = 50, offset = 0, filters = {}) {
  const params = new URLSearchParams({
    limit,
    offset,
    ...filters
  });

  const response = await fetch(`${API_BASE_URL}/api/posts?${params}`);

  if (!response.ok) {
    throw new Error("Failed to fetch posts");
  }

  return response.json();
}


/* -------------------------------------------------
   2. Fetch Sentiment Distribution
-------------------------------------------------- */
export async function fetchDistribution(hours = 24) {
  const response = await fetch(
    `${API_BASE_URL}/api/sentiment/distribution?hours=${hours}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch distribution");
  }

  return response.json();
}


/* -------------------------------------------------
   3. Fetch Aggregate Sentiment Data
-------------------------------------------------- */
export async function fetchAggregateData(period, startDate, endDate) {
  const params = new URLSearchParams({
    period
  });

  if (startDate) params.append("start_date", startDate);
  if (endDate) params.append("end_date", endDate);

  const response = await fetch(
    `${API_BASE_URL}/api/sentiment/aggregate?${params}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch aggregate data");
  }

  return response.json();
}


/* -------------------------------------------------
   4. WebSocket Connection
-------------------------------------------------- */
export function connectWebSocket(onMessage, onError, onClose) {
  const ws = new WebSocket(import.meta.env.VITE_WS_URL);

  ws.onopen = () => {
    console.log("WebSocket connected");
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };

  ws.onerror = (err) => {
    console.error("WebSocket error", err);
    onError?.(err);
  };

  ws.onclose = () => {
    console.log("WebSocket closed");
    onClose?.();
  };

  return ws;
}
