FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY streamlit_app.py .
# Copy debug config for vscode
COPY .vscode .vscode

EXPOSE 8501
EXPOSE 5678

# Default, run the stramlit app normally
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
# Keep the container running, do nothing. Used to run the streamlit app manually in debug mode once inside the container.
# CMD ["tail", "-f", "/dev/null"]
# Used to debug using vscode from the local machine
# CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
