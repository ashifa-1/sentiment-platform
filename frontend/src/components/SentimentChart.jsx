import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const COLORS = { positive: '#10b981', negative: '#ef4444', neutral: '#facc15' };

const SentimentChart = ({ data }) => (
  <div className="bg-[#25282c] border border-gray-700 p-6 rounded-sm shadow-xl">
    <h3 className="text-md mb-1 text-gray-400 font-mono uppercase tracking-wider">Sentiment Trend Over Time</h3>
    <p className="text-xs text-gray-600 mb-6 font-bold font-mono">[Line Chart - Last 24 Hours]</p>
    
    {/* minHeight ensures the chart doesn't collapse to 0 and throw errors */}
    <div className="h-72 w-full" style={{ minHeight: '300px' }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2d3135" vertical={false} />
          <XAxis 
            dataKey="time" 
            stroke="#4b5563" 
            fontSize={10} 
            tickLine={false} 
            axisLine={false}
          />
          <YAxis 
            stroke="#4b5563" 
            fontSize={10} 
            tickLine={false} 
            axisLine={false} 
          />
          <Tooltip 
            contentStyle={{backgroundColor: '#1a1c1e', border: '1px solid #374151', color: '#fff'}} 
          />
          <Line 
            type="monotone" 
            dataKey="positive" 
            stroke={COLORS.positive} 
            strokeWidth={2} 
            dot={false} 
            activeDot={{ r: 4 }}
          />
          <Line 
            type="monotone" 
            dataKey="negative" 
            stroke={COLORS.negative} 
            strokeWidth={2} 
            dot={false} 
            activeDot={{ r: 4 }}
          />
          <Line 
            type="monotone" 
            dataKey="neutral" 
            stroke={COLORS.neutral} 
            strokeWidth={2} 
            dot={false} 
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  </div>
);

export default SentimentChart;