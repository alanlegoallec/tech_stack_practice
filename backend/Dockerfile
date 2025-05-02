FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        libssl-dev \
        bash \
        curl \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Disable Poetry virtualenvs (use system environment inside container)
RUN poetry config virtualenvs.create false

# Copy the backend code
COPY . .

# Default to not installing dev dependencies
ARG INSTALL_DEV=false

# Install dependencies: include dev tools if INSTALL_DEV is true
RUN if [ "$INSTALL_DEV" = "true" ]; then \
        poetry install; \
    else \
        poetry install --only main; \
    fi

# Make scripts executable
RUN chmod +x scripts/install-vscode-extensions.sh \
    && chmod +x /app/wait-for-db.sh

# Optional: remove __pycache__ (keeps image clean)
RUN find . -type d -name "__pycache__" -exec rm -rf {} +

# Only expose the application port here (debug port managed in docker-compose)
EXPOSE 5001

# Start the backend
CMD ["./wait-for-db.sh", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "5001"]
