import React from 'react';

const COLORS = { positive: '#10b981', negative: '#ef4444', neutral: '#facc15' };

const LiveFeed = ({ posts }) => (
  <div className="card">
    <h3 style={{ margin: 0, fontSize: '14px', color: '#999', borderBottom: '1px solid #333', paddingBottom: '5px' }}>Recent Posts Feed </h3>
    
    <div className="scrollable-content">
      {posts.map((post, i) => (
        <div key={i} style={{ padding: '10px 0', borderBottom: '1px solid #131111ff' }}>
          <div className="w-2 h-10 shrink-0" style={{backgroundColor: COLORS[post.sentiment.label]}}></div>
          <div>
            <p style={{ margin: '0 0 5px 0', fontSize: '13px' }}>"{post.content.substring(0, 80)}..."</p>
            <span style={{ fontSize: '11px', color: '#666' }}>
              Author: {post.author} | {post.sentiment.label}
            </span>
          </div>
        </div>
      ))}
    </div>
  </div>
);

export default LiveFeed;