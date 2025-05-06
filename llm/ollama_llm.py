import os
import requests
from model.base import LLMInterface

class OllamaLLM(LLMInterface):
    def __init__(self):
        self.url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "mistral")

    def generate(self, prompt: str, max_new_tokens: int = 200) -> str:
        try:
            res = requests.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": max_new_tokens
                    }
                }
            )
            res.raise_for_status()
            return res.json()["response"].strip()
        except Exception as e:
            return f"[Ollama Error] {str(e)}"
