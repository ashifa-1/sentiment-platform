FROM python:3.9-slim

WORKDIR /app

# 1. Install ONLY essential system libs
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy requirements
COPY backend/requirements.txt ./backend_reqs.txt
COPY worker/requirements.txt ./worker_reqs.txt

# 3. Install with NO CACHE and specific CPU links
RUN pip install --no-cache-dir -r backend_reqs.txt -r worker_reqs.txt

# 4. Copy code
COPY . .