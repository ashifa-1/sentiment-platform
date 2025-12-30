import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const COLORS = { positive: '#10b981', negative: '#ef4444', neutral: '#facc15' };

const SentimentChart = ({ data }) => (
  <div className="bg-[#25282c] border border-gray-700 p-6 rounded-sm">
    <h3 className="text-md mb-2 text-gray-400 font-mono">Sentiment Trend Over Time</h3>
    <p className="text-xs text-gray-600 mb-6 font-bold font-mono">[Line Chart - Last 24 Hours]</p>
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2d3135" vertical={false} />
          <XAxis dataKey="time" stroke="#4b5563" fontSize={10} tickLine={false} />
          <YAxis stroke="#4b5563" fontSize={10} tickLine={false} axisLine={false} />
          <Tooltip contentStyle={{backgroundColor: '#1a1c1e', border: '1px solid #374151'}} />
          <Line type="monotone" dataKey="positive" stroke={COLORS.positive} strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="negative" stroke={COLORS.negative} strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="neutral" stroke={COLORS.neutral} strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  </div>
);

export default SentimentChart;