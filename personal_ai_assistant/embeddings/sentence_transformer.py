import os
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging
import json

logger = logging.getLogger(__name__)

class SentenceTransformerEmbeddings:
    def __init__(self, model_path: str):
        try:
            if os.path.isfile(model_path):
                # If model_path is a file, use its parent directory
                model_dir = os.path.dirname(model_path)
            else:
                model_dir = model_path

            logger.info(f"Attempting to load model from: {model_dir}")
            self.model = SentenceTransformer(model_dir)
            logger.info(f"Successfully loaded model from: {model_dir}")
        except Exception as e:
            logger.warning(f"Could not load model from {model_path}. Error: {str(e)}. Falling back to a default model.")
            try:
                # Try to load the default model
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Successfully loaded default model: all-MiniLM-L6-v2")
            except Exception as default_e:
                logger.error(f"Failed to load default model. Error: {str(default_e)}")
                raise

    def generate_embeddings(self, text: Union[str, List[str]]) -> np.ndarray:
        return self.model.encode(text)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        embedding1 = self.generate_embeddings(text1)
        embedding2 = self.generate_embeddings(text2)
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
