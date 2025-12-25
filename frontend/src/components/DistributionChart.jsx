import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

const COLORS = {
  positive: "#10b981",
  negative: "#ef4444",
  neutral: "#6b7280"
};

function DistributionChart({ data }) {
  if (!data) return <div className="card">No data available</div>;

  const chartData = Object.entries(data)
    .filter(([_, v]) => v > 0)
    .map(([k, v]) => ({ name: k, value: v }));

  return (
    <div className="card">
      <h3>Sentiment Distribution</h3>
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie data={chartData} dataKey="value" label>
            {chartData.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export default DistributionChart;
