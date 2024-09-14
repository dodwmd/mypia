from llama_cpp import Llama
from pathlib import Path
from personal_ai_assistant.database.db_manager import DatabaseManager

class LlamaCppInterface:
    def __init__(self, model_path: str, n_ctx: int = 512, n_threads: int = 4, db_manager: DatabaseManager = None):
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        self.llm = Llama(
            model_path=str(self.model_path),
            n_ctx=n_ctx,
            n_threads=n_threads
        )
        self.db_manager = db_manager

    def generate(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        cache_key = f"llm_generate_{prompt}_{max_tokens}_{temperature}"
        cached_result = self.db_manager.get_cached_data(cache_key) if self.db_manager else None
        
        if cached_result:
            return cached_result

        output = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["</s>", "\n"],
            echo=False
        )
        result = output['choices'][0]['text'].strip()

        if self.db_manager:
            self.db_manager.cache_data(cache_key, result)

        return result

    def summarize(self, text: str, max_length: int = 100) -> str:
        cache_key = f"llm_summarize_{text}_{max_length}"
        cached_result = self.db_manager.get_cached_data(cache_key) if self.db_manager else None
        
        if cached_result:
            return cached_result

        prompt = f"Summarize the following text in {max_length} words or less:\n\n{text}\n\nSummary:"
        summary = self.generate(prompt, max_tokens=max_length * 2)

        if self.db_manager:
            self.db_manager.cache_data(cache_key, summary)

        return summary
