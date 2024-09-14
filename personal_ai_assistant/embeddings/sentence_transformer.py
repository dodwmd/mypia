from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union

class SentenceTransformerEmbeddings:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for the given text or list of texts.
        
        :param texts: A single text string or a list of text strings
        :return: A numpy array of embeddings
        """
        return self.model.encode(texts)

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute the cosine similarity between two texts.
        
        :param text1: First text
        :param text2: Second text
        :return: Cosine similarity score
        """
        embedding1 = self.generate_embeddings(text1)
        embedding2 = self.generate_embeddings(text2)
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
