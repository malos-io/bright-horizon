FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Cloud Run uses PORT env variable (defaults to 8080)
ENV PORT=8080
EXPOSE 8080

# Run the application with dynamic port
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
