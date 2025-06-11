FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory
COPY . .

# Create data directory and set permissions
RUN mkdir -p /app/data && \
    chmod 777 /app/data

EXPOSE 8000

CMD ["uvicorn", "src.graphql.app:app", "--host", "0.0.0.0", "--port", "8000"] 