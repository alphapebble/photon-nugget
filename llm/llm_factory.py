import os
from model.ollama_llm import OllamaLLM
from model.transformer_llm import TransformersLLM

def get_llm():
    if os.getenv("USE_OLLAMA", "true").lower() == "true":
        return OllamaLLM()
    return TransformersLLM()
