# VedAstroPy API - Google Cloud Run Deployment
# Optimized for FastAPI with Swiss Ephemeris

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Swiss Ephemeris
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create ephemeris data directory
RUN mkdir -p /app/ephe

# Copy Swiss Ephemeris file (de421.bsp for planetary positions)
COPY de421.bsp /app/ephe/de421.bsp

# Copy application code
COPY . .

# Set Swiss Ephemeris path
ENV SWISSEPH_PATH=/app/ephe

# Expose port (Cloud Run uses PORT env variable)
ENV PORT=8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run FastAPI with uvicorn
# Using 2 workers for better performance
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 2
