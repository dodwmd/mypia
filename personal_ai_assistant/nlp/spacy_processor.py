import spacy
from typing import List, Dict, Any

class SpacyProcessor:
    def __init__(self, model: str = "en_core_web_sm"):
        self.nlp = spacy.load(model)

    def analyze_text(self, text: str) -> Dict[str, Any]:
        doc = self.nlp(text)
        return {
            "tokens": [token.text for token in doc],
            "lemmas": [token.lemma_ for token in doc],
            "pos_tags": [token.pos_ for token in doc],
            "named_entities": [(ent.text, ent.label_) for ent in doc.ents],
            "noun_chunks": [chunk.text for chunk in doc.noun_chunks],
            "sentences": [sent.text for sent in doc.sents]
        }

    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        doc = self.nlp(text)
        return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    def get_noun_chunks(self, text: str) -> List[str]:
        doc = self.nlp(text)
        return [chunk.text for chunk in doc.noun_chunks]

    def get_sentences(self, text: str) -> List[str]:
        doc = self.nlp(text)
        return [sent.text for sent in doc.sents]

    def get_similar_words(self, word: str, n: int = 5) -> List[str]:
        return [w for w, _ in self.nlp(word).vocab.vectors.most_similar(self.nlp(word).vector, n=n)]

    def get_word_vector(self, word: str) -> List[float]:
        return self.nlp(word).vector.tolist()
