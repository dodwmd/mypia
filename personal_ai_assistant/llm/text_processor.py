from typing import List, Dict
from .llama_cpp_interface import LlamaCppInterface

class TextProcessor:
    def __init__(self, llm):
        self.llm = llm

    def process(self, text):
        # Add your text processing logic here
        # For now, we'll just return the input text
        return text
