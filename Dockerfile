FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*
# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
# Startup script
RUN echo '#!/bin/bash\n\
ollama serve &\n\
echo "Waiting for Ollama..."\n\
sleep 10\n\
echo "Pulling Qwen 2.5B instruct model..."\n\
ollama pull qwen2.5:0.5b-instruct-q6_K\n\
python -m src.main\n' > /app/start.sh && chmod +x /app/start.sh
EXPOSE 8000
CMD ["/app/start.sh"]