FROM python:3.11-slim-bookworm

WORKDIR /app

# Install required system packages with security best practices
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose API port
EXPOSE 8000

# Run the application
CMD ["python", "src/main.py", "api"]
