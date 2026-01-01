import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const TrendChart = ({ data = [] }) => {
  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <h3 style={{ 
        borderBottom: '1px solid #374151', 
        paddingBottom: '0.5rem', 
        textTransform: 'uppercase', 
        fontSize: '14px',
        marginBottom: '1rem' 
      }}>
        Sentiment Trend Over Time
      </h3>
      
      {/* CRITICAL FIX: The wrapper div MUST have a fixed height.
        Your console error "height(-1)" proves this container was 0px.
      */}
      <div className="chart-container" style={{ width: '100%', height: '350px', position: 'relative' }}>
        {data && data.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
              <XAxis 
                dataKey="time" 
                stroke="#9ca3af" 
                fontSize={12} 
                tickLine={false} 
                axisLine={false} 
              />
              <YAxis 
                stroke="#9ca3af" 
                fontSize={12} 
                tickLine={false} 
                axisLine={false} 
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#e8e9ebff', 
                  border: '1px solid #374151', 
                  borderRadius: '4px' 
                }}
                itemStyle={{ fontSize: '12px' }}
              />
              <Legend verticalAlign="top" height={36}/>
              <Line 
                type="monotone" 
                dataKey="positive" 
                stroke="#10b981" 
                strokeWidth={2} 
                dot={false} 
                activeDot={{ r: 4 }} 
              />
              <Line 
                type="monotone" 
                dataKey="negative" 
                stroke="#ef4444" 
                strokeWidth={2} 
                dot={false} 
                activeDot={{ r: 4 }} 
              />
              <Line 
                type="monotone" 
                dataKey="neutral" 
                stroke="#facc15" 
                strokeWidth={2} 
                dot={false} 
                activeDot={{ r: 4 }} 
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div style={{ 
            height: '100%', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            color: '#6b7280' 
          }}>
            [Line Chart - Last 24 Hours] Waiting for data points...
          </div>
        )}
      </div>
    </div>
  );
};

export default TrendChart;