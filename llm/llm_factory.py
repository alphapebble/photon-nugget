import os
from llm.ollama_llm import OllamaLLM
from llm.transformer_llm import TransformersLLM

def get_llm():
    if os.getenv("USE_OLLAMA", "true").lower() == "true":
        return OllamaLLM()
    return TransformersLLM()
