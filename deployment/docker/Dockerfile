FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV SOLAR_SAGE_ENV=production
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 8000
EXPOSE 8502

# Run the application
CMD ["python", "-m", "cli.main", "server"]
