FROM python:3.11-slim

WORKDIR /app

# Install bash and dependencies needed for Poetry and your app
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl build-essential && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Poetry (no virtualenvs)
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

# Copy the full source code
COPY . .

# Install the local package (core code)
RUN poetry install --only-root

# Make the install-vscode-extensions.sh script executable (optional)
RUN chmod +x scripts/install-vscode-extensions.sh

# Expose the main frontend port only (others go in docker-compose)
EXPOSE ${CONTAINER_STREAMLIT_PORT}

# Run the app with the configured port
CMD ["sh", "-c", "streamlit run frontend/streamlit_app.py --server.port=${CONTAINER_STREAMLIT_PORT} --server.address=0.0.0.0"]
