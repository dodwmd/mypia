from typing import Optional
from personal_ai_assistant.llm.llama_cpp_interface import LlamaCppInterface


class TextProcessor:
    def __init__(self, llm_interface: Optional[LlamaCppInterface] = None):
        self.llm_interface = llm_interface

    # ... (rest of the code remains unchanged)
