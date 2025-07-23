# Discord Bot - Python only
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot application files
COPY app.py .

# Create empty data file (bot will populate it)
RUN echo '{"daily_results": {}, "guild_settings": {}}' > wordle_data.json

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port (though bot doesn't need it, Railway might expect it)
EXPOSE 8080

# Run the Discord bot
CMD ["python3", "app.py"]
