# src/llm_service.py
import aiohttp
import asyncio
import json
import logging
from typing import Dict, Any

# Set up logging to help with debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # Ollama runs on localhost:11434 by default
        self.ollama_url = "http://localhost:11434"
        self.model_name = "qwen3:0.6b"
        
    async def check_health(self) -> bool:
        """
        Check if Ollama service is running and responsive.
        This is like knocking on the door to see if anyone's home.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_url}/api/tags", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Check if our model is loaded
                        models = [model['name'] for model in data.get('models', [])]
                        return self.model_name in models
                    return False
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def generate_response(self, message: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        """
        Generate a response using the Qwen model.
        This is where we actually talk to the AI model.
        """
        payload = {
            "model": self.model_name,
            "prompt": message,
            "stream": False,  # Get complete response at once
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=60  # Give it time to think
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', 'No response generated')
                    else:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error: {response.status} - {error_text}")
        except asyncio.TimeoutError:
            raise Exception("Request timed out - model might be too slow")
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    async def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        Useful for monitoring and debugging.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_url}/api/show",
                    json={"name": self.model_name}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": "Could not retrieve model info"}
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {"error": str(e)}