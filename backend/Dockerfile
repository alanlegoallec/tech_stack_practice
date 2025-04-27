FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

COPY wait-for-db.sh .
RUN chmod +x wait-for-db.sh

CMD ["./wait-for-db.sh", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]

# Idle command to keep the container running, used when connecting with the vscode debugger from within the container
# CMD ["tail", "-f", "/dev/null"]
# Used to run the debugger by connecting to the container from the local machine
# CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:${FLASK_DEBUG_PORT}", "--wait-for-client", "app.py"]