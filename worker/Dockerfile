FROM python:3.9-slim

WORKDIR /app

# Copy requirements first (better for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# IMPORTANT: Copy everything from the worker folder into /app
COPY . .

# Ensure main.py is in the root of /app
CMD ["python", "main.py"]