# Multi-stage Dockerfile for Face Shape Hairstyle Recommendation System
# Stage 1: Build dependencies
# Stage 2: Production image

FROM python:3.11-slim AS base

# System dependencies for OpenCV and MediaPipe
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server/ ./server/
COPY client/ ./client/
COPY ml/models/ ./ml/models/
COPY database/ ./database/

# Create upload directory
RUN mkdir -p server/uploads

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/api/auth/profile || exit 1

# Run with Gunicorn
CMD ["gunicorn", "server.wsgi:app", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
