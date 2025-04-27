FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including OpenSSL development headers
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python build tools
RUN pip install --upgrade pip setuptools wheel

# Copy only pyproject.toml first (for better Docker cache)
COPY pyproject.toml ./

# Install your backend and its dependencies
RUN pip install .

# Copy the rest of the backend project
COPY . .

# Make the wait-for-db.sh script executable
RUN chmod +x /app/wait-for-db.sh

# Remove any __pycache__ folders that might have been copied in
RUN find . -type d -name "__pycache__" -exec rm -rf {} +

# Expose ports
EXPOSE 5001
EXPOSE 5678

# Normal startup
CMD ["./wait-for-db.sh", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "5001"]
