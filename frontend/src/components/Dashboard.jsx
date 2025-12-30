import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import DistributionChart from './DistributionChart';
import SentimentChart from './SentimentChart';
import LiveFeed from './LiveFeed';

const COLORS = { positive: '#10b981', negative: '#ef4444', neutral: '#facc15' };

const Dashboard = () => {
  const [distribution, setDistribution] = useState([{ name: 'Positive', value: 0 }, { name: 'Negative', value: 0 }, { name: 'Neutral', value: 0 }]);
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
    <div className="dashboard-viewport">
      {/* 1. Header */}
      <div className="header-card">
        <h1 style={{ margin: 0, fontSize: '1.2rem' }}>Real-Time Sentiment Analysis Dashboard</h1>
        <div style={{ display: 'flex', gap: '20px', fontSize: '12px', color: '#888' }}>
          <span>[Status: <span style={{color: '#10b981'}}>● LIVE</span>]</span>
          <span>[Last Update: {lastUpdate}]</span>
        </div>
      </div>

      {/* 2. Middle Grid: Distribution and Scrollable Feed */}
      <div className="middle-row">
        <DistributionChart data={distribution} />
        <LiveFeed posts={posts} />
      </div>

      {/* 3. Sentiment Trend */}
      <div className="card" style={{ flex: '0.7' }}>
        <SentimentChart data={trend} />
      </div>

      {/* 4. Bottom Metrics */}
      <div className="metrics-row">
        {['Total', 'Positive', 'Negative', 'Neutral'].map((label, idx) => (
          <div key={label} className="card" style={{ padding: '10px' }}>
          	<p style={{ margin: '0 0 10px 0', fontSize: '12px', fontWeight: 'bold', color: '#999' }}>{label}</p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ width: '10px', height: '10px', backgroundColor: label === 'Total' ? '#3b82f6' : Object.values(COLORS)[idx-1] }}></div>
              <span style={{ fontSize: '24px', fontWeight: 'bold' }}>
                {label === 'Total' ? total : distribution[idx-1]?.value || 0}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
