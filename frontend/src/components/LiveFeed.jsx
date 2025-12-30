import React from 'react';

const COLORS = { positive: '#10b981', negative: '#ef4444', neutral: '#facc15' };

const LiveFeed = ({ posts }) => (
  <div className="bg-[#25282c] border border-gray-700 p-6 rounded-sm">
    <h3 className="text-md mb-4 border-b border-gray-700 pb-2 text-gray-400 font-mono">Recent Posts Feed [Live scrolling]</h3>
    <div className="space-y-4 h-64 overflow-y-auto pr-2 custom-scrollbar font-mono">
      {posts.map((post, i) => (
        <div key={i} className="flex gap-3 items-start border-b border-gray-800 pb-3">
          <div className="w-2 h-10 shrink-0" style={{backgroundColor: COLORS[post.sentiment.label]}}></div>
          <div>
            <p className="text-xs text-gray-300 leading-relaxed mb-1 italic">"{post.content.substring(0, 80)}..."</p>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest">
              Author: {post.author} | {post.sentiment.label}
            </p>
          </div>
        </div>
      ))}
    </div>
  </div>
);

export default LiveFeed;