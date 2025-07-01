# src/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import sys
import asyncio

# Add the parent directory to sys.path so Python can find our modules
# This is crucial for the import system to work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm_service import LLMService

# Initialize FastAPI app
app = FastAPI(
    title="Qwen LLM API",
    description="API wrapper for Qwen3 0.6B model using Ollama",
    version="1.0.0"
)

# Initialize LLM service
llm_service = LLMService()

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.7

class ChatResponse(BaseModel):
    response: str
    model: str
    tokens_used: Optional[int] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Simple health check to verify the service is running.
    This is crucial for Render's deployment process.
    """
    try:
        # Test if Ollama is responsive
        is_ready = await llm_service.check_health()
        if is_ready:
            return {"status": "healthy", "model": "qwen3:0.6b"}
        else:
            raise HTTPException(status_code=503, detail="LLM service not ready")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# Main chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and return the model's response.
    This is where the magic happens - we take user input and get AI output.
    """
    try:
        response = await llm_service.generate_response(
            message=request.message,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return ChatResponse(
            response=response,
            model="qwen3:0.6b"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

# Get model information
@app.get("/model/info")
async def model_info():
    """
    Return information about the loaded model.
    Useful for debugging and monitoring.
    """
    try:
        info = await llm_service.get_model_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")

# Run the application
if __name__ == "__main__":
    # Get port from environment variable (Render requirement)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)