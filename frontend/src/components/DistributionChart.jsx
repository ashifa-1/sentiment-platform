import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const COLORS = { positive: '#10b981', negative: '#ef4444', neutral: '#facc15' };

const DistributionChart = ({ data }) => {
  const total = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="card">
      <h3 style={{ borderBottom: '1px solid #374151', paddingBottom: '0.5rem', textTransform: 'uppercase', fontSize: '14px' }}>
        Sentiment Distribution
      </h3>
      <div className="chart-container">
        {total > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[entry.name.toLowerCase()]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{backgroundColor: '#1a1c1e', border: '1px solid #374151', color: '#fff'}} />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div style={{ padding: '2rem', textAlign: 'center', color: '#666' }}>Waiting for data stream...</div>
        )}
      </div>
    </div>
  );
};

export default DistributionChart;