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

# Copy only requirements and pyproject.toml first (for better Docker cache)
COPY requirements.txt pyproject.toml ./

# Install Python dependencies (from requirements.txt and/or pyproject.toml)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend project
COPY . .

# Install your backend as a package (editable mode for dev, normal for prod)
RUN pip install --no-cache-dir .

# Remove any __pycache__ folders that might have been copied in
RUN find . -type d -name "__pycache__" -exec rm -rf {} +

# Expose ports
EXPOSE 8501
EXPOSE 5678


RUN chmod +x wait-for-db.sh

# Normal startup
CMD ["./wait-for-db.sh", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "5001"]

# Idle command to keep the container running, used when connecting with the vscode debugger from within the container
# CMD ["tail", "-f", "/dev/null"]
