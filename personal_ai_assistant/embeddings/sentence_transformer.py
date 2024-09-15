import os
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging

logger = logging.getLogger(__name__)

class SentenceTransformerEmbeddings:
    def __init__(self, model_path: str):
        try:
            self.model = SentenceTransformer(model_path)
        except Exception as e:
            logger.warning(f"Could not load model from {model_path}. Error: {str(e)}. Falling back to a default model.")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def generate_embeddings(self, text: Union[str, List[str]]) -> np.ndarray:
        return self.model.encode(text)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        embedding1 = self.generate_embeddings(text1)
        embedding2 = self.generate_embeddings(text2)
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
