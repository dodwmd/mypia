from llama_cpp import Llama


class LlamaCppInterface:
    def __init__(self, model_path, db_manager=None):
        self.model = Llama(model_path=model_path)
        self.db_manager = db_manager

    def generate_text(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        response = self.model(prompt, max_tokens=max_tokens, temperature=temperature)
        generated_text = response['choices'][0]['text']
        # Log the interaction
        self.db_manager.log_llm_interaction(prompt, generated_text)
        return generated_text

    def answer_question(self, context: str, question: str, max_tokens: int = 100) -> str:
        prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
        return self.generate_text(prompt, max_tokens)

    def summarize_text(self, text: str, max_length: int = 100) -> str:
        prompt = f"Please summarize the following text in no more than {max_length} words:\n\n{text}\n\nSummary:"
        return self.generate_text(prompt, max_tokens=max_length)

    def generate_tasks(self, description: str, num_tasks: int = 3) -> list:
        prompt = f"Based on the following description, generate {num_tasks} tasks:\n\n{description}\n\nTasks:"
        tasks_text = self.generate_text(prompt, max_tokens=100 * num_tasks)
        return tasks_text.strip().split('\n')

    def analyze_sentiment(self, text: str) -> dict:
        prompt = f"Analyze the sentiment of the following text and provide scores for positive, negative, and neutral sentiments (scores should sum to 1.0):\n\n{text}\n\nSentiment scores:"
        sentiment_text = self.generate_text(prompt, max_tokens=50)
        # Parse the sentiment scores (this is a simple implementation and might need to be adjusted based on the actual output format)
        sentiment_scores = {}
        for line in sentiment_text.strip().split('\n'):
            sentiment, score = line.split(':')
            sentiment_scores[sentiment.strip().lower()] = float(score.strip())
        return sentiment_scores
