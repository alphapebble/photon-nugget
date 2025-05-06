import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from llm.base import LLMInterface

class TransformersLLM(LLMInterface):
    def __init__(self):
        model_path = os.getenv("MODEL_PATH", "./models/mistral-7b-instruct")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )

    def generate(self, prompt: str, max_new_tokens: int = 200) -> str:
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)[len(prompt):].strip()
        except Exception as e:
            return f"[Transformers Error] {str(e)}"
