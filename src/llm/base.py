from abc import ABC, abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    def generate(self, prompt: str, max_new_tokens: int = 200) -> str:
        pass
