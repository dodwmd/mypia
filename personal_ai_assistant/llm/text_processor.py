from typing import List, Dict
from .llama_cpp_interface import LlamaCppInterface

class TextProcessor:
    def __init__(self, llm: LlamaCppInterface):
        self.llm = llm

    def generate_text(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        """
        Generate text based on the given prompt.
        
        :param prompt: The input prompt for text generation
        :param max_tokens: Maximum number of tokens to generate
        :param temperature: Controls randomness in generation. Higher values make output more random.
        :return: Generated text
        """
        return self.llm.generate(prompt, max_tokens=max_tokens, temperature=temperature)

    def summarize_text(self, text: str, max_length: int = 100, format: str = 'paragraph') -> str:
        """
        Summarize the given text.
        
        :param text: The input text to summarize
        :param max_length: Maximum length of the summary in words
        :param format: Format of the summary ('paragraph' or 'bullet_points')
        :return: Summarized text
        """
        prompt = f"Summarize the following text in {max_length} words or less. "
        prompt += "Format the summary as a paragraph." if format == 'paragraph' else "Format the summary as bullet points."
        prompt += f"\n\nText: {text}\n\nSummary:"
        
        return self.llm.generate(prompt, max_tokens=max_length * 2)

    def answer_question(self, context: str, question: str, max_tokens: int = 100) -> str:
        """
        Answer a question based on the given context.
        
        :param context: The context information
        :param question: The question to answer
        :param max_tokens: Maximum number of tokens for the answer
        :return: Answer to the question
        """
        prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
        return self.llm.generate(prompt, max_tokens=max_tokens)

    def generate_tasks(self, description: str, num_tasks: int = 3) -> List[str]:
        """
        Generate a list of tasks based on the given description.
        
        :param description: Description of the overall task or project
        :param num_tasks: Number of tasks to generate
        :return: List of generated tasks
        """
        prompt = f"Generate {num_tasks} tasks for the following project:\n\n{description}\n\nTasks:"
        tasks_text = self.llm.generate(prompt, max_tokens=num_tasks * 20)
        return [task.strip() for task in tasks_text.split('\n') if task.strip()]

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze the sentiment of the given text.
        
        :param text: The input text to analyze
        :return: Dictionary containing sentiment scores
        """
        prompt = f"Analyze the sentiment of the following text and provide scores for positive, negative, and neutral sentiments (each ranging from 0 to 1):\n\n{text}\n\nSentiment scores:"
        sentiment_text = self.llm.generate(prompt, max_tokens=50)
        
        sentiment_scores = {}
        for line in sentiment_text.split('\n'):
            if ':' in line:
                key, value = line.split(':')
                sentiment_scores[key.strip().lower()] = float(value.strip())
        
        return sentiment_scores
