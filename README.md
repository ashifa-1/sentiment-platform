# Real-Time Sentiment Analysis Platform

This project is a high-performance, distributed sentiment analysis platform designed to process live data streams and provide immediate emotional insights. It utilizes a microservices architecture to ingest simulated social media data, perform Natural Language Processing (NLP) to categorize sentiments as positive, negative, or neutral, and visualize these trends on a dynamic, responsive dashboard. Built to handle high-velocity data, the system ensures that every post is analyzed and stored for both real-time monitoring and historical trend analysis.

## Features List
* **Real-Time Data Ingestion**: Continuous simulation of social media streams with metadata like authors and timestamps.
* **NLP Sentiment Analysis**: Automated classification of text into Positive, Negative, and Neutral categories.
* **Live Dashboard**: A "fit-to-screen" React UI featuring a scrollable live feed and real-time Recharts visualizations.
* **Microservices Architecture**: Six decoupled services managed via Docker for high availability and modularity.
* **WebSocket Integration**: Instant UI updates without page refreshes for a truly "live" experience.
* **Persistent Storage**: Time-series optimized database storage for historical sentiment tracking.

## Architecture Overview
The system follows a pipeline: Ingestion -> Analysis -> Storage -> API -> Visualization. A detailed breakdown of components and data flow can be found in [ARCHITECTURE.md](./ARCHITECTURE.md).

## Prerequisites

* **Hardware**: 4GB RAM minimum.
* **Network**: Ports 3000 (Frontend) and 8000 (Backend) must be available.
* **API Keys**: If using an external LLM (like OpenAI or HuggingFace), keys must be placed in the `.env` file.

## Quick Start

#### 1. Clone repository
git clone https://github.com/ashifa-1/sentiment-platform

cd sentiment-platform

#### 2. Copy environment template
cp .env.example .env

#### 3. Edit .env file with your API keys

#### 4. Start all services
docker-compose up -d

#### 5. Wait for services to be healthy (30-60 seconds)
docker-compose ps

#### 6. Access dashboard

#### 7. Stop services
docker-compose down

## Configuration

The following environment variables are used in the .env file:

#### DATABASE_URL: 
The connection string for the PostgreSQL database.

#### VITE_API_URL: 
The URL of the backend API (use the forwarded address in Codespaces).

#### STREAM_DELAY: 
Controls the speed of the ingestion service (in seconds).

#### SECRET_KEY: 
Used for security and authentication hashing.

## API Documentation

**GET /api/posts**: Retrieves the most recent analyzed posts from the database.

**GET /api/distribution**: Returns the count and percentage of each sentiment category.

**GET /api/health**: Returns 200 OK if the backend and DB connections are healthy.

**WS /ws/updates**: WebSocket endpoint for receiving live sentiment updates.

## Testing Instructions
To run the automated test suite and check code coverage:

-> docker-compose exec backend pytest --cov=app --cov-report=term-missing

## Troubleshooting

**Blank Charts:** Ensure Port 8000 is set to Public in the GitHub Codespaces Ports tab.

**Dashboard shows "Error" status:** Check if the backend container is running using docker-compose logs backend.

**Database connection refused:** The DB takes longer to start than the API; restart the API container if it fails on the first boot.

## Project Structure

|--SENTIMENT-PLATFORM/
|--backend/
¦   +-- app
¦       +-- api/         
¦           +-- routes.py
¦           +-- websocket.py
¦       +-- models/
¦           +-- database.py
¦       +-- services/  
¦           +-- sentiment_analyzer.py
¦           +-- aggregator.py        
¦           +-- alerting.py          
¦   +-- main.py
¦   +-- tests/
¦   +-- requirements.txt
¦
+-- worker/
¦   +-- requirements.txt
¦   +-- worker.py
¦
+-- ingester/
¦   +-- Dockerfile
¦   +-- ingester.py
¦
+-- frontend/
    +-- src/         
        +-- components/
        ¦   +-- Dashboard.jsx
        ¦   +-- SentimentChart.jsx
        ¦   +-- DistributionChart.jsx
        ¦   +-- LiveFeed.jsx
        +-- services/
            +-- api.js
        +-- App.css
        +-- App.jsx
        +-- index.css
        +-- main.jsx
    +-- .gitignore
    +-- Dockerfile
    +-- eslint.config.js
    +-- index.html
    +-- package-lock.json
    +-- package.json
    +-- vite.config.js
|--.dockerignore
|--.env
|--.env.example
|--ARCHITECTURE.md
|--docker-compose.yml
|--Dockerfile
|--README.md


## Phase 6: Quality Assurance
This project maintains a **75% test coverage** across the backend services.

### Running Tests
To execute the test suite and generate a coverage report, run:

docker-compose exec backend /bin/sh -c "export PYTHONPATH=$PYTHONPATH:/app && pytest backend/tests --cov=backend/app"

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.