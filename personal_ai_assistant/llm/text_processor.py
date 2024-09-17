from personal_ai_assistant.llm.llama_cpp_interface import LlamaCppInterface


class TextProcessor:
    def __init__(self, llm: LlamaCppInterface):
        self.llm = llm

    async def summarize_text(self, text: str, max_length: int = 100) -> str:
        prompt = f"Summarize the following text in no more than {max_length} words:\n\n{text}"
        summary = await self.llm.generate(prompt, max_tokens=max_length * 2)  # Assuming 2 tokens per word on average
        return summary.strip()

    async def generate_text(self, prompt: str, max_length: int = 100) -> str:
        generated_text = await self.llm.generate(prompt, max_tokens=max_length * 2)
        return generated_text.strip()

    # ... (rest of the code remains unchanged)
