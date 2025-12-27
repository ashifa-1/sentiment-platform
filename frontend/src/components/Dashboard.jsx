import { useEffect, useState } from "react";
import {
  fetchPosts,
  fetchDistribution,
  fetchAggregateData,
  connectWebSocket
} from "../services/api";

import DistributionChart from "./DistributionChart";
import SentimentTrendChart from "./SentimentTrendChart";
import MetricsCard from "./MetricsCard";
import "./Dashboard.css";

function Dashboard() {
  const [distribution, setDistribution] = useState(null);
  const [trendData, setTrendData] = useState([]);
  const [recentPosts, setRecentPosts] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const [lastUpdate, setLastUpdate] = useState(null);

  const [metrics, setMetrics] = useState({
    total: 0,
    positive: 0,
    negative: 0,
    neutral: 0
  });

  /* ---------------- Initial REST Load ---------------- */
  useEffect(() => {
    async function loadInitialData() {
      try {
        const dist = await fetchDistribution(24);
        setDistribution(dist);

        if (dist?.distribution) {
          const d = dist.distribution;
          const total =
            d.positive + d.negative + d.neutral;

          setMetrics({
            total,
            positive: d.positive,
            negative: d.negative,
            neutral: d.neutral
          });
        }

        const agg = await fetchAggregateData("hour");
        setTrendData(agg?.data || []);

        const posts = await fetchPosts(10, 0);
        setRecentPosts(posts?.posts || []);
      } catch (err) {
        console.error("Initial data load failed:", err);
      }
    }

    loadInitialData();
  }, []);

  /* ---------------- WebSocket ---------------- */
  useEffect(() => {
    const ws = connectWebSocket(
      (message) => {
        setLastUpdate(new Date());

        if (message.type === "connected") {
          setConnectionStatus("connected");
        }

        if (message.type === "new_post") {
          setRecentPosts((prev) => [
            message.data,
            ...prev.slice(0, 9)
          ]);
        }

        if (message.type === "metrics_update") {
          const d = message.data.last_24_hours;
          const total = d.positive + d.negative + d.neutral;

          setMetrics({
            total,
            positive: d.positive,
            negative: d.negative,
            neutral: d.neutral
          });

          setDistribution({
            distribution: d
          });
        }
      },
      () => setConnectionStatus("disconnected"),
      () => setConnectionStatus("disconnected")
    );

    return () => ws.close();
  }, []);

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <h1>Real-Time Sentiment Analysis Dashboard</h1>
        <div className="status-bar">
          <span className={`status-dot ${connectionStatus}`}>●</span>
          <span>{connectionStatus}</span>
          <span className="last-update">
            Last Update:{" "}
            {lastUpdate ? lastUpdate.toLocaleTimeString() : "--"}
          </span>
        </div>
      </div>

      {/* Top Row */}
      <div className="row">
        <DistributionChart data={distribution} />

        <div className="card recent-posts">
          <h3>Recent Posts</h3>
          {recentPosts.length === 0 && <p>No posts yet</p>}
          {recentPosts.map((post) => (
            <div key={post.post_id} className="post-item">
              <p>{post.content.slice(0, 120)}...</p>
              <span className={`sentiment ${post.sentiment?.label}`}>
                {post.sentiment?.label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Trend */}
      <SentimentTrendChart data={trendData} />

      {/* Metrics */}
      <div className="metrics-row">
        <MetricsCard title="Total" value={metrics.total} />
        <MetricsCard title="Positive" value={metrics.positive} />
        <MetricsCard title="Negative" value={metrics.negative} />
        <MetricsCard title="Neutral" value={metrics.neutral} />
      </div>
    </div>
  );
}

export default Dashboard;
