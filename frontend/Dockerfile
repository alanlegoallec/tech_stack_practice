FROM python:3.11-slim

WORKDIR /app

# Install bash and dependencies needed for Poetry and your app
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl build-essential && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy the full source code
COPY . .

# Install dependencies using Poetry (no virtualenvs)
RUN poetry config virtualenvs.create false && poetry install

# Make the install-vscode-extensions.sh script executable (optional)
RUN chmod +x scripts/install-vscode-extensions.sh

# Expose the main frontend port only (others go in docker-compose)
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
