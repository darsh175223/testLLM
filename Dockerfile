# Dockerfile
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies
# We need curl to download Ollama
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
# This downloads and installs the Ollama binary
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create startup script
# This script will start both Ollama and our API
RUN echo '#!/bin/bash\n\
# Start Ollama in the background\n\
ollama serve &\n\
\n\
# Wait for Ollama to start\n\
echo "Waiting for Ollama to start..."\n\
sleep 10\n\
\n\
# Pull the Qwen model\n\
echo "Pulling Qwen3 0.6B model..."\n\
ollama pull qwen3:0.6b\n\
\n\
# Start the FastAPI application\n\
echo "Starting FastAPI application..."\n\
python -m src.main\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose the port that Render will use
EXPOSE 8000

# Run our startup script
CMD ["/app/start.sh"]