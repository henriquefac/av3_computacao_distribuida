FROM python:3.11-slim

WORKDIR /app

# Copy requirements file
COPY requirements-rest.txt .
RUN pip install --no-cache-dir -r requirements-rest.txt

# Create data directory
RUN mkdir -p /app/data && \
    chmod 777 /app/data

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 