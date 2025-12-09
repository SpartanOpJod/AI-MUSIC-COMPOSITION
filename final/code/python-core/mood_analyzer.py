import numpy as np
from functools import lru_cache
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from config import Config


class MoodAnalyzer:
    def __init__(self):
        self.sentiment_model = pipeline(
            "sentiment-analysis",
            model=Config.SENTIMENT_MODEL,
            device=-1
        )
        self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.moods = np.array([
            "happy",
            "sad",
            "calm",
            "energetic",
            "mysterious",
            "romantic"
        ])
        self.mood_embeddings = self.embedding_model.encode(
            self.moods, normalize_embeddings=True
        )
        self.high_energy_words = np.array([
            "excited",
            "workout",
            "dance",
            "party",
            "energetic"
        ])
        self.low_energy_words = np.array([
            "tired",
            "relaxed",
            "calm",
            "sleepy",
            "slow"
        ])
        self.sentiment_adjust = {
            "p": 1,
            "n": -1
        }

    @lru_cache(maxsize=5000)
    def _embed_text(self, text: str):
        return self.embedding_model.encode(
            [text],
            normalize_embeddings=True
        )

    @lru_cache(maxsize=5000)
    def _sentiment_text(self, text: str):
        result = self.sentiment_model(text)[0]
        return result["label"].lower(), round(result["score"], 2)

    def _classify_mood(self, text: str):
        embedding = self._embed_text(text)
        sims = cosine_similarity(
            embedding,
            self.mood_embeddings
        )[0]
        return self.moods[sims.argmax()]

    def _calculate_energy(self, words: set, sentiment: str) -> int:
        base = 5
        high = np.isin(self.high_energy_words, list(words)).sum()
        low = np.isin(self.low_energy_words, list(words)).sum()
        adjust = self.sentiment_adjust.get(sentiment[0], 0)
        total = base + (2 * high) - (2 * low) + adjust
        return int(np.clip(total, 1, 10))

    def _analyze_single(self, text: str):
        text = text.lower().strip()
        sentiment, score = self._sentiment_text(text)
        mood = self._classify_mood(text)
        words = set(text.split())
        energy = self._calculate_energy(words, sentiment)
        return {
            "sentiment": sentiment,
            "sentiment_score": score,
            "mood": mood,
            "energy": energy
        }

    def analyze(self, texts):
        if isinstance(texts, str):
            return self._analyze_single(texts)
        results = []
        for text in texts:
            result = self._analyze_single(text)
            results.append(result)
        return results
