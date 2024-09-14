from llama_cpp import Llama
from pathlib import Path

class LlamaCppInterface:
    def __init__(self, model_path: str, n_ctx: int = 512, n_threads: int = 4):
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        self.llm = Llama(
            model_path=str(self.model_path),
            n_ctx=n_ctx,
            n_threads=n_threads
        )

    def generate(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        output = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["</s>", "\n"],
            echo=False
        )
        return output['choices'][0]['text'].strip()

    def summarize(self, text: str, max_length: int = 100) -> str:
        prompt = f"Summarize the following text in {max_length} words or less:\n\n{text}\n\nSummary:"
        return self.generate(prompt, max_tokens=max_length * 2)
