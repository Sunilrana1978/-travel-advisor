FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent and server code
COPY travel_agent/ ./travel_agent/
COPY server.py .

# Cloud Run injects GOOGLE_API_KEY (or Vertex AI env vars) at runtime via Secret Manager
ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
