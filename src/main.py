# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import sys
import asyncio

# Ensure Python finds our package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm_service import LLMService

app = FastAPI(
    title="Qwen LLM API",
    description="API wrapper for Qwen 2.5B instruct model using Ollama",
    version="1.0.0"
)

# === CORS configuration ===
origins = [
    "http://localhost:3000",
    # add other origins here if needed, e.g. "https://your-production-domain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],  # or specify ["Content-Type", "Authorization", ...]
)
# ==========================

llm_service = LLMService(model_name="qwen2.5:0.5b-instruct-q6_K")

class ChatRequest(BaseModel):
    message: str
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.7

class ChatResponse(BaseModel):
    response: str
    model: str
    tokens_used: Optional[int] = None

@app.get("/health")
async def health_check():
    try:
        is_ready = await llm_service.check_health()
        if is_ready:
            return {"status": "healthy", "model": llm_service.model_name}
        else:
            raise HTTPException(status_code=503, detail="LLM service not ready")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {e}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        resp_text = await llm_service.generate_response(
            message=request.message,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        return ChatResponse(
            response=resp_text,
            model=llm_service.model_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

@app.get("/model/info")
async def model_info():
    try:
        return await llm_service.get_model_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {e}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
