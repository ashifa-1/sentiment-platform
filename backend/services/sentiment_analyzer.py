from transformers import pipeline
import os


class SentimentAnalyzer:
    """
    Unified interface for sentiment analysis using multiple model backends
    """

    def __init__(self, model_type: str = "local", model_name: str = None):
        if model_type != "local":
            raise NotImplementedError("Only local model supported for now")

        # Sentiment model
        self.sentiment_model_name = model_name or os.getenv(
            "HUGGINGFACE_MODEL",
            "distilbert-base-uncased-finetuned-sst-2-english"
        )

        self.sentiment_pipeline = pipeline(
            task="text-classification",
            model=self.sentiment_model_name,
            device=-1
        )

        # Emotion model
        self.emotion_model_name = os.getenv(
            "EMOTION_MODEL",
            "j-hartmann/emotion-english-distilroberta-base"
        )

        self.emotion_pipeline = pipeline(
            task="text-classification",
            model=self.emotion_model_name,
            top_k=None,
            device=-1
        )

    async def analyze_sentiment(self, text: str) -> dict:
        if not text or not text.strip():
            return {
                "sentiment_label": "neutral",
                "confidence_score": 0.0,
                "model_name": self.sentiment_model_name
            }

        result = self.sentiment_pipeline(text[:512])[0]

        label = result["label"].lower()
        score = float(result["score"])

        if label not in ["positive", "negative"]:
            label = "neutral"

        return {
            "sentiment_label": label,
            "confidence_score": min(max(score, 0.0), 1.0),
            "model_name": self.sentiment_model_name
        }

    async def analyze_emotion(self, text: str) -> dict:
        if text is None or not text.strip():
            raise ValueError("Text cannot be empty")

        if len(text.strip()) < 10:
            return {
                "emotion": "neutral",
                "confidence_score": 0.0,
                "model_name": self.emotion_model_name
            }

        results = self.emotion_pipeline(text[:512])[0]

        top_emotion = max(results, key=lambda x: x["score"])

        emotion = top_emotion["label"].lower()
        score = float(top_emotion["score"])

        allowed_emotions = {
            "joy", "sadness", "anger", "fear", "surprise", "neutral"
        }

        if emotion not in allowed_emotions:
            emotion = "neutral"

        return {
            "emotion": emotion,
            "confidence_score": min(max(score, 0.0), 1.0),
            "model_name": self.emotion_model_name
        }


    async def batch_analyze(self, texts: list[str]) -> list[dict]:
        if not texts:
            return []

        # Initialize results with placeholders
        results = [None] * len(texts)

        valid_texts = []
        valid_indexes = []

        for idx, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text[:512])
                valid_indexes.append(idx)
            else:
                # Handle empty / invalid text
                results[idx] = {
                    "sentiment_label": "neutral",
                    "confidence_score": 0.0,
                    "model_name": self.sentiment_model_name
                }

        # Run batch inference only on valid texts
        if valid_texts:
            outputs = self.sentiment_pipeline(valid_texts)

            for i, output in enumerate(outputs):
                label = output["label"].lower()
                score = float(output["score"])

                if label not in ["positive", "negative"]:
                    label = "neutral"

                results[valid_indexes[i]] = {
                    "sentiment_label": label,
                    "confidence_score": min(max(score, 0.0), 1.0),
                    "model_name": self.sentiment_model_name
                }

        return results
    