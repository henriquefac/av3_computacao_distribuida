FROM python:3.10-slim-buster

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create data directory and ensure it's writable
RUN mkdir -p /app/data && \
    chmod 777 /app/data

# Expose port 8000
EXPOSE 8000

# Start the application
CMD ["python", "src/soup/app.py"] 