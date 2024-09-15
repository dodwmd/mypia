import spacy
import logging
from typing import List

logger = logging.getLogger(__name__)

class SpacyProcessor:
    def __init__(self, model='en_core_web_sm'):
        try:
            self.nlp = spacy.load(model)
        except OSError:
            logger.warning(f"SpaCy model '{model}' not found. Attempting to download...")
            spacy.cli.download(model)
            self.nlp = spacy.load(model)

    def process(self, text):
        doc = self.nlp(text)
        return {
            'tokens': [token.text for token in doc],
            'entities': [(ent.text, ent.label_) for ent in doc.ents],
            'noun_chunks': [chunk.text for chunk in doc.noun_chunks],
            'sentences': [sent.text for sent in doc.sents]
        }

    def get_entities(self, text):
        doc = self.nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]

    def get_noun_chunks(self, text):
        doc = self.nlp(text)
        return [chunk.text for chunk in doc.noun_chunks]

    def get_sentences(self, text):
        doc = self.nlp(text)
        return [sent.text for sent in doc.sents]

    def get_similar_words(self, word: str, n: int = 5) -> List[str]:
        return [w for w, _ in self.nlp(word).vocab.vectors.most_similar(self.nlp(word).vector, n=n)]

    def get_word_vector(self, word: str) -> List[float]:
        return self.nlp(word).vector.tolist()
