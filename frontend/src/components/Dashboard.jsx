import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import DistributionChart from './DistributionChart';
import SentimentChart from './SentimentChart';
import LiveFeed from './LiveFeed';

// ADD THIS LINE HERE:
const COLORS = { positive: '#10b981', negative: '#ef4444', neutral: '#facc15' };

const Dashboard = () => {
  const [distribution, setDistribution] = useState([
    { name: 'Positive', value: 0 },
    { name: 'Negative', value: 0 },
    { name: 'Neutral', value: 0 },
  ]);
  const [trend, setTrend] = useState([]);
  const [posts, setPosts] = useState([]);
  const [status, setStatus] = useState('connecting');
  const [lastUpdate, setLastUpdate] = useState('--:--:--');

  const fetchData = async () => {
    try {
      const [dist, postsData, aggregate] = await Promise.all([
        apiService.fetchDistribution(),
        apiService.fetchPosts(10),
        apiService.fetchAggregateData('minute')
      ]);
      
      setDistribution([
        { name: 'Positive', value: dist.data.positive || 0 },
        { name: 'Negative', value: dist.data.negative || 0 },
        { name: 'Neutral', value: dist.data.neutral || 0 },
      ]);
      setPosts(postsData.data.posts || []);
      setTrend(aggregate.data.data.map(d => ({
          ...d,
          time: new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      })));
      setStatus('live');
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (err) {
      console.error("Dashboard Fetch Error:", err);
      setStatus('error');
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const total = distribution.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="min-h-screen bg-[#1a1c1e] text-[#e1e1e1] p-8 font-mono">
      {/* Header */}
      <div className="border-l-4 border-blue-500 bg-[#25282c] p-6 mb-8 shadow-xl">
        <h1 className="text-xl font-bold mb-2 uppercase tracking-tight">Real-Time Sentiment Analysis Dashboard</h1>
        <div className="flex gap-8 text-sm text-gray-400">
          <span>[Status: <span className={status === 'live' ? 'text-green-400' : 'text-red-400'}>● {status.toUpperCase()}</span>]</span>
          <span>[Last Update: [{lastUpdate}]]</span>
        </div>
      </div>

      {/* Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <DistributionChart data={distribution} />
        <LiveFeed posts={posts} />
      </div>

      <SentimentChart data={trend} />

      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-8">
        {['Total', 'Positive', 'Negative', 'Neutral'].map((label, idx) => (
          <div key={label} className="bg-[#25282c] border border-gray-700 p-5 rounded-sm shadow-lg">
            <p className="text-sm font-bold text-gray-400 mb-4">{label}</p>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3" style={{backgroundColor: label === 'Total' ? '#3b82f6' : Object.values(COLORS)[idx-1]}}></div>
              <span className="text-2xl font-bold tracking-tighter">
                {label === 'Total' ? total : (distribution[idx-1]?.value || 0)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;