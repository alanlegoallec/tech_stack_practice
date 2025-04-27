FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client && \
    rm -rf /var/lib/apt/lists/*

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

EXPOSE 5001

RUN chmod +x wait-for-db.sh

CMD ["./wait-for-db.sh", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "5001"]


# Idle command to keep the container running, used when connecting with the vscode debugger from within the container
# CMD ["tail", "-f", "/dev/null"]
# Used to run the debugger by connecting to the container from the local machine
# CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:${FLASK_DEBUG_PORT}", "--wait-for-client", "app.py"]