FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements-graphql.txt .
RUN pip install --no-cache-dir -r requirements-graphql.txt

# Create data directory
RUN mkdir -p /app/data && \
    chmod 777 /app/data

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 