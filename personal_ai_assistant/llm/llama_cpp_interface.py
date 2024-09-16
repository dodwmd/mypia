import os
from llama_cpp import Llama


class LlamaCppInterface:
    def __init__(self, model_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
        self.llm = Llama(model_path=model_path)

    def generate(self, prompt: str, max_tokens: int = 100) -> str:
        output = self.llm(prompt, max_tokens=max_tokens)
        return output['choices'][0]['text']

    # Add other methods as needed
