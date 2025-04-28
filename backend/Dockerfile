# Use the official Python image as a base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies including OpenSSL development headers and PostgreSQL client
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    libssl-dev \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Install Python build tools (pip, setuptools, wheel)
RUN pip install --upgrade pip setuptools wheel

# Copy only the pyproject.toml first (for better Docker cache when dependencies change)
COPY pyproject.toml ./

# Install the backend and its dependencies (using pip to install the package)
RUN pip install .

# Copy the rest of the backend project (including source code)
COPY . .

# Make the wait-for-db.sh script executable
RUN chmod +x scripts/install-vscode-extensions.sh

# Make the wait-for-db.sh script executable
RUN chmod +x /app/wait-for-db.sh

# Remove any __pycache__ directories that might have been copied in
RUN find . -type d -name "__pycache__" -exec rm -rf {} +

# Expose the port for the backend API (FastAPI/uvicorn)
EXPOSE 5001

# Expose the port for the VSCode debugger
EXPOSE 5678

# Default startup command
CMD ["./wait-for-db.sh", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "5001"]
