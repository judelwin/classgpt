# Placeholder Dockerfile for the Embedding Worker
# This will be fully implemented in a later task.
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY embedding-worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY embedding-worker/ .
# Copy core directory from ingestion-service
COPY ingestion-service/core /app/core

# Set PYTHONPATH so /app is in the module search path
ENV PYTHONPATH=/app

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port (if needed for monitoring)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the Celery worker
CMD ["celery", "-A", "celery_config.celery_app", "worker", "--loglevel=info", "-Q", "embedding_queue"] 