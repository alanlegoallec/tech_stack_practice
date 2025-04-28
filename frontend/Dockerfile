FROM python:3.11-slim

WORKDIR /app

# Install bash to ensure compatibility with bash scripts
RUN apt-get update && apt-get install -y bash

# Copy only the files needed for dependency installation first (for Docker cache efficiency)
COPY pyproject.toml .
# If you use a build backend like setuptools, also copy setup.cfg or setup.py if present

# Install your package and its dependencies
RUN pip install .[dev]

# Copy the rest of your frontend code
COPY . .

# Make the install-vscode-extensions.sh script executable
RUN chmod +x scripts/install-vscode-extensions.sh

# Expose the port for the Streamlit app
EXPOSE 8501

# Expose the port for the VSCode debugger
EXPOSE 5678

# Default startup command to run the Streamlit app
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Used to debug using vscode from the local machine
# CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
