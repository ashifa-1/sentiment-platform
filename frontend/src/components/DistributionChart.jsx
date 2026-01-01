import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const COLORS = { 
  positive: '#10b981', 
  negative: '#ef4444', 
  neutral: '#facc15' 
};

const DistributionChart = ({ data = [] }) => {
  // Safe reduction to calculate total
  const total = data.reduce((sum, item) => sum + (item.value || 0), 0);

  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <h3 style={{ 
        borderBottom: '1px solid #374151', 
        paddingBottom: '0.5rem', 
        textTransform: 'uppercase', 
        fontSize: '14px',
        marginBottom: '1rem' 
      }}>
        Sentiment Distribution
      </h3>
      
      {/* CRITICAL FIX: The wrapper div MUST have a fixed height (like 300px) 
        or ResponsiveContainer will collapse to 0px.
      */}
      <div className="chart-container" style={{ width: '100%', height: '300px', position: 'relative' }}>
        {total > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie 
                data={data} 
                innerRadius={60} 
                outerRadius={80} 
                paddingAngle={5} 
                dataKey="value"
                animationDuration={1000}
              >
                {data.map((entry, index) => {
                  const colorKey = entry.name ? entry.name.toLowerCase() : 'neutral';
                  return (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={COLORS[colorKey] || COLORS.neutral} 
                    />
                  );
                })}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#e8e9ebff', 
                  border: '1px solid #374151', 
                  borderRadius: '4px',
                  color: '#100101ff' 
                }} 
                itemStyle={{ color: '#110606ff' }}
              />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div style={{ 
            height: '100%', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            color: '#6b7280' 
          }}>
            Waiting for data stream...
          </div>
        )}
      </div>
    </div>
  );
};

export default DistributionChart;