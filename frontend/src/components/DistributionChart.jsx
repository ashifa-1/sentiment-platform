import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const COLORS = { positive: '#10b981', negative: '#ef4444', neutral: '#facc15' };

const DistributionChart = ({ data }) => {
  const total = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="bg-[#25282c] border border-gray-700 p-6 rounded-sm">
      <h3 className="text-md mb-4 border-b border-gray-700 pb-2 text-gray-400 font-mono">Sentiment Distribution</h3>
      <div className="h-64 flex items-center justify-center">
        {total > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} innerRadius={0} outerRadius={80} dataKey="value">
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[entry.name.toLowerCase()]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{backgroundColor: '#1a1c1e', border: '1px solid #374151'}} />
            </PieChart>
          </ResponsiveContainer>
        ) : <div className="text-gray-600 italic font-mono text-sm">Waiting for data stream...</div>}
      </div>
    </div>
  );
};

export default DistributionChart;