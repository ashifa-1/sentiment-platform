import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

function formatTime(ts) {
  return new Date(ts).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit"
  });
}

function SentimentTrendChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="card">No trend data</div>;
  }

  return (
    <div className="card">
      <h3>Sentiment Trend (Last 24 Hours)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" tickFormatter={formatTime} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line dataKey="positive" stroke="#10b981" />
          <Line dataKey="negative" stroke="#ef4444" />
          <Line dataKey="neutral" stroke="#6b7280" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default SentimentTrendChart;
