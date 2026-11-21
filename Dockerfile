# Multi-stage production Dockerfile for StyleAI
FROM python:3.12-slim as builder

WORKDIR /app

# Install system build dependencies & OpenCV library dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt gunicorn

# Production runner stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime OpenCV & MediaPipe C++ dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source code
COPY . .

# Create uploads & logs directories
RUN mkdir -p server/uploads logs && chmod -R 777 server/uploads logs

EXPOSE 5000

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "120", "wsgi:app"]
