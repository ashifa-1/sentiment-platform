<h1> Real-Time Sentiment Analysis Platform</h1>

<h2>System Architecture</h2>

<p>
This platform is designed as a <b>real-time sentiment analysis system</b> that processes streaming social media–like data end-to-end.
All services are containerized and orchestrated using <b>Docker Compose</b> to ensure consistency, scalability, and ease of deployment.
</p>

<h2>🧩 Architecture Diagram</h2>

<pre>
[ Data Ingestion Service ]
            |
            v
     [ Redis Cache ]
            |
            v
[ NLP Processing Service ]
            |
            v
   [ PostgreSQL DB ]
            |
            v
[ FastAPI Backend API ]
     (REST + WebSocket)
            |
            v
[ React Frontend Dashboard ]
</pre>

<h2> Component Descriptions</h2>

<h3> Data Ingestion Service</h3>
<ul>
  <li>Python-based producer</li>
  <li>Simulates live social media posts</li>
  <li>Generates post text, author, and timestamp</li>
  <li>Publishes raw data to Redis</li>
</ul>

<h3> NLP Processing Service</h3>
<ul>
  <li>Consumes data from Redis</li>
  <li>Applies NLP techniques to analyze sentiment</li>
  <li>Classifies posts as <b>Positive</b>, <b>Negative</b>, or <b>Neutral</b></li>
</ul>

<h3> PostgreSQL Database</h3>
<ul>
  <li>Primary persistent storage</li>
  <li>Stores analyzed posts and historical data</li>
  <li>Supports aggregation and trend analysis</li>
</ul>

<h3> Backend API (FastAPI)</h3>
<ul>
  <li>Acts as the central system hub</li>
  <li>Provides REST APIs for historical data</li>
  <li>Maintains WebSocket connections for real-time updates</li>
  <li>Asynchronous and high-performance</li>
</ul>

<h3> Frontend (React)</h3>
<ul>
  <li>Fit-to-screen responsive dashboard</li>
  <li>Live-updating sentiment charts using Recharts</li>
  <li>Real-time scrolling feed of analyzed posts</li>
</ul>

<h3> Cache Service (Redis)</h3>
<ul>
  <li>High-speed message broker</li>
  <li>Decouples ingestion and processing services</li>
  <li>Ensures low-latency data flow</li>
</ul>


<h2> Data Flow</h2>

<ol>
  <li><b>Ingestion:</b> A simulated post is generated and sent to Redis.</li>
  <li><b>Processing:</b> NLP service analyzes the text and assigns sentiment.</li>
  <li><b>Storage:</b> The processed post is stored in PostgreSQL.</li>
  <li><b>Serving:</b> Backend API pushes updates instantly to the frontend using WebSockets.</li>
</ol>

<h2> Technology Justification</h2>

<ul>
  <li><b>FastAPI:</b> Chosen for its async support and high throughput, ideal for WebSocket-based real-time systems.</li>
  <li><b>PostgreSQL:</b> Reliable relational database with strong support for aggregation queries and data integrity.</li>
  <li><b>Standard CSS (Flexbox/Grid):</b> Used instead of Tailwind to ensure consistent layouts without build overhead.</li>
  <li><b>GitHub Codespaces:</b> Provides a standardized cloud-based Docker environment, avoiding local OS and Docker Desktop limitations.</li>
</ul>

<h2>🧱 Database Schema</h2>

<table border="1" cellpadding="8" cellspacing="0">
  <tr>
    <th>Column</th>
    <th>Type</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>id</td>
    <td>UUID</td>
    <td>Primary Key</td>
  </tr>
  <tr>
    <td>text</td>
    <td>TEXT</td>
    <td>Post content</td>
  </tr>
  <tr>
    <td>sentiment</td>
    <td>VARCHAR</td>
    <td>Sentiment label</td>
  </tr>
  <tr>
    <td>author</td>
    <td>VARCHAR</td>
    <td>Simulated user handle</td>
  </tr>
  <tr>
    <td>timestamp</td>
    <td>TIMESTAMP</td>
    <td>UTC ingestion time</td>
  </tr>
</table>

<h2> API Design</h2>

<h3>REST Endpoints</h3>
<ul>
  <li><code>GET /api/posts</code> – Fetch last N posts</li>
  <li><code>GET /api/distribution</code> – Sentiment distribution summary</li>
</ul>

<h3>WebSocket</h3>
<ul>
  <li><code>WS /ws/updates</code> – Pushes real-time sentiment updates to UI</li>
</ul>

<p><b>Data Format:</b> JSON (used across REST and WebSocket)</p>


<h2> Scalability Considerations</h2>

<ul>
  <li>Processing service is stateless, enabling horizontal scaling.</li>
  <li>Database indexes on <code>timestamp</code> and <code>sentiment</code> ensure fast queries at scale.</li>
</ul>

<h2> Security Considerations</h2>

<ul>
  <li>Sensitive credentials are stored only in <code>.env</code> files.</li>
  <li>No secrets are hardcoded in the repository.</li>
  <li>CORS is restricted to the authorized frontend origin.</li>
</ul>


<h2> Conclusion</h2>

<p>
This architecture delivers a <b>scalable, low-latency, and production-ready</b> real-time sentiment analysis system.
It demonstrates modern backend design, real-time data handling, and clean service separation.
</p>