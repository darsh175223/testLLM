# src/llm_service.py
import aiohttp
import asyncio
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, model_name: str = "qwen2.5:0.5b-instruct-q6_K"):
        self.ollama_url = "http://localhost:11434"
        self.model_name = model_name

    async def check_health(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_url}/api/tags", timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = [m['name'] for m in data.get('models', [])]
                        return self.model_name in models
                    return False
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def generate_response(self, message: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        payload = {
            "model": self.model_name,
            "prompt": message,
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": temperature}
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=60
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get('response', '')
                    error = await resp.text()
                    raise Exception(f"Ollama error {resp.status}: {error}")
        except asyncio.TimeoutError:
            raise Exception("Request timed out")
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise

    async def get_model_info(self) -> Dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_url}/api/show",
                    json={"name": self.model_name}
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    return {"error": "Could not retrieve model info"}
        except Exception as e:
            logger.error(f"Info fetch failed: {e}")
            return {"error": str(e)}
