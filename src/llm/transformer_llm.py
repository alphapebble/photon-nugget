import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from llm.base import LLMInterface

class TransformersLLM(LLMInterface):
    def __init__(self):
        # Get models directory from environment variable with fallback to default
        models_dir = os.getenv("SOLAR_SAGE_MODELS_DIR", "./models")
        model_name = os.getenv("SOLAR_SAGE_LLM_MODEL", "mistral-7b-instruct")

        # Construct the full model path
        model_path = os.path.join(models_dir, model_name)

        print(f"Loading model from: {model_path}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto",
            local_files_only=True
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
