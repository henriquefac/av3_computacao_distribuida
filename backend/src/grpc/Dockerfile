FROM python:3.9-slim

WORKDIR /app

# Install system dependencies and protoc
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements-grpc.txt /app/
RUN pip install --no-cache-dir -r requirements-grpc.txt

# Install grpcio-tools for the gRPC Python plugin
RUN pip install --no-cache-dir grpcio-tools==1.44.0

# Copy the proto file and server implementation
COPY src/grpc/music_service.proto .
COPY src/grpc/server.py .

# Generate gRPC code
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. music_service.proto

# Create data directory
RUN mkdir -p /app/data && \
    chmod 777 /app/data

EXPOSE 50051

CMD ["python", "server.py"] 