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
  const [metrics, setMetrics] = useState({
    total: 0,
    positive: 0,
    negative: 0,
    neutral: 0
  });

  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    async function loadInitialData() {
      const dist = await fetchDistribution(24);
      const trend = await fetchAggregateData("hour");
      const posts = await fetchPosts(10, 0);

      setDistribution(dist.distribution);
      setTrendData(trend.data);
      setRecentPosts(posts.posts);

      setMetrics({
        total: dist.total,
        positive: dist.distribution.positive,
        negative: dist.distribution.negative,
        neutral: dist.distribution.neutral
      });

      setLastUpdate(new Date());
    }

    loadInitialData();

    const ws = connectWebSocket(
      (msg) => {
        if (msg.type === "connected") {
          setConnectionStatus("connected");
        }

        if (msg.type === "new_post") {
          setRecentPosts((prev) => [msg.data, ...prev.slice(0, 9)]);
          setLastUpdate(new Date());
        }

        if (msg.type === "metrics_update") {
          setMetrics(msg.data.last_hour);
          setLastUpdate(new Date());
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
            Last Update: {lastUpdate ? lastUpdate.toLocaleTimeString() : "--"}
          </span>
        </div>
      </div>

      {/* Top Row */}
      <div className="row">
        <DistributionChart data={distribution} />

        <div className="card recent-posts">
          <h3>Recent Posts</h3>
          {recentPosts.map((post) => (
            <div key={post.post_id} className="post-item">
              <p>{post.content.slice(0, 100)}...</p>
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
