import os
from transformers import pipeline
import httpx # for external API calls

class SentimentAnalyzer:
    def __init__(self, model_type='local', model_name=None):
        self.model_type = model_type
        # Load local models if selected
        if self.model_type == 'local':
            # Sentiment Analysis Model
            hf_model = model_name or os.getenv("HUGGINGFACE_MODEL")
            self.sentiment_pipe = pipeline("text-classification", model=hf_model, device=-1) # -1 is CPU
            
            # Emotion Detection Model
            emotion_model = os.getenv("EMOTION_MODEL")
            self.emotion_pipe = pipeline("text-classification", model=emotion_model, device=-1)

    async def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment of input text (up to 512 tokens)."""
        if not text or len(text.strip()) == 0:
            return {"sentiment_label": "neutral", "confidence_score": 0.0, "model_name": "none"}

        if self.model_type == 'local':
            # Run inference
            result = self.sentiment_pipe(text[:512])[0]
            label = result['label'].lower()
            
            # Normalize labels to pos/neg/neu
            final_label = "neutral"
            if "pos" in label: final_label = "positive"
            elif "neg" in label: final_label = "negative"
            
            return {
                "sentiment_label": final_label,
                "confidence_score": round(result['score'], 4),
                "model_name": os.getenv("HUGGINGFACE_MODEL")
            }
        
        # Placeholder for External LLM (Groq) logic as per requirements
        return {"sentiment_label": "neutral", "confidence_score": 0.5, "model_name": "external"}

    async def analyze_emotion(self, text: str) -> dict:
        """Detect primary emotion in text."""
        if self.model_type == 'local':
            result = self.emotion_pipe(text[:512])[0]
            return {
                "emotion": result['label'], # joy, anger, etc.
                "confidence_score": round(result['score'], 4),
                "model_name": os.getenv("EMOTION_MODEL")
            }
        return {"emotion": "neutral", "confidence_score": 0.5, "model_name": "external"}