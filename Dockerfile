# Bot deployment only - no web interface
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy bot files
COPY app.py .
COPY wordle_data.json .

# Run the bot
CMD ["python3", "app.py"]
