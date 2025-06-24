# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed for libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY ingestion-service/requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the shared directory first
COPY shared/ /app/shared

# Copy the rest of the application's code into the container
COPY ingestion-service/ /app

# Set PYTHONPATH so /app is in the module search path
ENV PYTHONPATH=/app

# Make port 8001 available to the world outside this container
EXPOSE 8001

# Run main.py when the container launches
# Use --host 0.0.0.0 to make it accessible from outside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"] 