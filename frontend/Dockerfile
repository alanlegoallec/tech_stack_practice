FROM python:3.11

WORKDIR /app

# Copy only the files needed for dependency installation first (for Docker cache efficiency)
COPY pyproject.toml .
# If you use a build backend like setuptools, also copy setup.cfg or setup.py if present

# Install your package and its dependencies
RUN pip install .

# Copy the rest of your frontend code
COPY . .

EXPOSE 8501
EXPOSE 5678

CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]


# Keep the container running, do nothing. Used to run the streamlit app manually in debug mode once inside the container.
# CMD ["tail", "-f", "/dev/null"]
# Used to debug using vscode from the local machine
# CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
