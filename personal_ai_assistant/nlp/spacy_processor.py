import spacy
from typing import List, Dict
from personal_ai_assistant.config import settings


class SpacyProcessor:
    def __init__(self, model_name: str = settings.spacy_model):
        self.nlp = spacy.load(model_name)

    def process_text(self, text: str) -> Dict:
        doc = self.nlp(text)
        return {
            'entities': [(ent.text, ent.label_) for ent in doc.ents],
            'tokens': [token.text for token in doc],
            'pos_tags': [(token.text, token.pos_) for token in doc],
            'noun_chunks': [chunk.text for chunk in doc.noun_chunks],
        }

    def extract_entities(self, text: str) -> List[Dict]:
        doc = self.nlp(text)
        return [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]

    def get_noun_chunks(self, text: str) -> List[str]:
        doc = self.nlp(text)
        return [chunk.text for chunk in doc.noun_chunks]

    def get_pos_tags(self, text: str) -> List[Dict]:
        doc = self.nlp(text)
        return [{'text': token.text, 'pos': token.pos_} for token in doc]
