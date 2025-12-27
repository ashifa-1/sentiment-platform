from transformers import pipeline
import os


class SentimentAnalyzer:
    def __init__(self):
        self.sentiment_model_name = os.getenv(
            "HUGGINGFACE_MODEL",
            "distilbert-base-uncased-finetuned-sst-2-english"
        )

        self.sentiment_pipeline = pipeline(
            "text-classification",
            model=self.sentiment_model_name,
            device=-1
        )

        self.emotion_model_name = os.getenv(
            "EMOTION_MODEL",
            "j-hartmann/emotion-english-distilroberta-base"
        )

        self.emotion_pipeline = pipeline(
            "text-classification",
            model=self.emotion_model_name,
            top_k=None,
            device=-1
        )

    def analyze_sentiment(self, text: str) -> dict:
        if not text or not text.strip():
            return {
                "sentiment_label": "neutral",
                "confidence_score": 0.0,
                "model_name": self.sentiment_model_name
            }

        result = self.sentiment_pipeline(text[:512])[0]

        label = result["label"].lower()
        if label not in ["positive", "negative"]:
            label = "neutral"

        return {
            "sentiment_label": label,
            "confidence_score": float(result["score"]),
            "model_name": self.sentiment_model_name
        }

    def analyze_emotion(self, text: str) -> dict:
        if not text or len(text.strip()) < 10:
            return {
                "emotion": "neutral",
                "confidence_score": 0.0,
                "model_name": self.emotion_model_name
            }

        results = self.emotion_pipeline(text[:512])[0]
        top = max(results, key=lambda x: x["score"])

        return {
            "emotion": top["label"].lower(),
            "confidence_score": float(top["score"]),
            "model_name": self.emotion_model_name
        }
