# mood_analyzer.py
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer, util
import numpy as np
from config import Config

class MoodAnalyzer:
    def __init__(self):
        # Load Hugging Face sentiment model
        self.sentiment_tokenizer = AutoTokenizer.from_pretrained(Config.SENTIMENT_MODEL)
        self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(
            Config.SENTIMENT_MODEL
        ).to(Config.DEVICE)

        # Load embedding model
        self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL, device=Config.DEVICE)

        # Define mood categories
        self.mood_categories = ["happy", "sad", "calm", "energetic", "mysterious", "romantic"]

        # Pre-compute embeddings for moods
        self.mood_embeddings = self.embedding_model.encode(self.mood_categories, convert_to_tensor=True)

        # High/low energy keywords
        self.high_energy_words = {"excited", "energetic", "party", "workout", "jump", "dance"}
        self.low_energy_words = {"calm", "relaxed", "chill", "sleep", "tired"}

    def analyze_sentiment(self, text: str):
        """Get sentiment + confidence"""
        inputs = self.sentiment_tokenizer(
            text, return_tensors="pt", truncation=True, max_length=Config.MAX_LENGTH
        ).to(Config.DEVICE)
        outputs = self.sentiment_model(**inputs)
        scores = torch.nn.functional.softmax(outputs.logits, dim=-1)

        labels = ["negative", "neutral", "positive"]
        score_dict = {labels[i]: scores[0][i].item() for i in range(len(labels))}
        sentiment = max(score_dict, key=score_dict.get)
        return sentiment, score_dict[sentiment]

    def classify_mood(self, text: str):
        """Find closest mood using embeddings"""
        text_embedding = self.embedding_model.encode(text, convert_to_tensor=True)
        similarity_scores = util.pytorch_cos_sim(text_embedding, self.mood_embeddings)[0]
        best_idx = int(torch.argmax(similarity_scores))
        return self.mood_categories[best_idx]

    def calculate_energy(self, text: str, sentiment: str):
        """Energy = sentiment base + keyword adjustment (1-10 scale)"""
        energy = 5
        if sentiment == "positive":
            energy += 2
        elif sentiment == "negative":
            energy -= 1

        words = text.lower().split()
        energy += sum(1 for w in words if w in self.high_energy_words)
        energy -= sum(1 for w in words if w in self.low_energy_words)

        return max(1, min(10, energy))

    def analyze(self, text: str):
        sentiment, confidence = self.analyze_sentiment(text)
        mood = self.classify_mood(text)
        energy = self.calculate_energy(text, sentiment)

        from music_parameters import map_to_music
        music_params = map_to_music(mood, sentiment, energy)

        return {
            "text": text,
            "sentiment": sentiment,
            "sentiment_confidence": confidence,
            "mood": mood,
            "energy": energy,
            **music_params
        }
