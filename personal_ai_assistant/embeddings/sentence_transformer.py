from sentence_transformers import SentenceTransformer
from personal_ai_assistant.config import settings
import logging

logger = logging.getLogger(__name__)


class SentenceTransformerEmbeddings:
    def __init__(self, model_name: str = settings.embedding_model):
        self.model = SentenceTransformer(model_name)

    # ... (rest of the code remains unchanged)
