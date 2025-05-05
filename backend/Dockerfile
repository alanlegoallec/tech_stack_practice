FROM python:3.13-slim

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

# Copy only pyproject.toml and poetry.lock first
COPY pyproject.toml poetry.lock ./

# Default to not installing dev dependencies
ARG INSTALL_DEV=false

# Install dependencies: include dev tools if INSTALL_DEV is true
RUN if [ "$INSTALL_DEV" = "true" ]; then \
        poetry install --no-root; \
    else \
        poetry install --only main --no-root; \
    fi

# Copy the backend code
COPY . .

# Install the local package (core code)
RUN poetry install --only-root

# Make scripts executable
RUN chmod +x scripts/install-vscode-extensions.sh \
    && chmod +x scripts/wait-for-db.sh

# Optional: remove __pycache__ (keeps image clean)
RUN find . -type d -name "__pycache__" -exec rm -rf {} +

# Only expose the application port (EXPOSE is mostly for documentation)
EXPOSE 5000

# Set default command — uses the environment variable
CMD ["sh", "-c", "./scripts/wait-for-db.sh uvicorn backend.main:app --host 0.0.0.0 --port 5000"]
