FROM python:3.10-slim-buster

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements-soap.txt .
RUN pip install --no-cache-dir -r requirements-soap.txt

# Create data directory
RUN mkdir -p /app/data && \
    chmod 777 /app/data

EXPOSE 8000

CMD ["python", "app.py"] 