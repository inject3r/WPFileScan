FROM python:3.11-slim

LABEL maintainer="inject3r"
LABEL description="WPFileScan - WordPress Brute Force File Finder"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directories for logs and downloads
RUN mkdir -p /app/logs /app/downloads

# Set entrypoint
ENTRYPOINT ["python", "main.py"]

# Default command (show help)
CMD ["-h"]