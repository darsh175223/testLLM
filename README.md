# README.md
# LLM API with Qwen 0.6B on Render

This project deploys a REST API wrapper around the Qwen 0.6B language model using Ollama and FastAPI, hosted on Render.

## Local Development (Windows)

1. Create and activate virtual environment:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt

# LLM API with Qwen 2.5B instruct model on Render

## Changes from 0.6B to 2.5B instruct
- Updated `model_name` in code and startup script to `qwen2.5:0.5b-instruct-q6_K`
- Changed pull command in Dockerfile to `ollama pull qwen2.5:0.5b-instruct-q6_K`
