# backend/app/services/sentiment_analyzer.py
from transformers import pipeline
import os
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """
    Unified interface for sentiment analysis using multiple model backends
    with threshold logic to support Neutral categorization.
    """
    
    def __init__(self, model_type: str = 'local', model_name: str = None):
        self.model_type = model_type
        # Set the threshold: If confidence is below 0.6, we call it neutral
        self.neutral_threshold = 0.60 
        
        if self.model_type == 'local':
            # Load default models from env if not provided
            self.sentiment_model_name = model_name or os.getenv("HUGGINGFACE_MODEL", "distilbert-base-uncased-finetuned-sst-2-english")
            self.emotion_model_name = os.getenv("EMOTION_MODEL", "j-hartmann/emotion-english-distilroberta-base")
            
            logger.info(f"Loading local models: {self.sentiment_model_name}...")
            
            # Initialize Pipelines
            # device=-1 means CPU (use 0 for GPU if available)
            self.sentiment_pipeline = pipeline("text-classification", model=self.sentiment_model_name, device=-1)
            self.emotion_pipeline = pipeline("text-classification", model=self.emotion_model_name, device=-1)
            
        elif self.model_type == 'external':
            self.api_key = os.getenv("EXTERNAL_LLM_API_KEY")
            logger.info("External LLM mode initialized")

    async def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment (Positive/Negative/Neutral) with threshold logic"""
        if not text:
            raise ValueError("Input text cannot be empty")

        if self.model_type == 'local':
            # Run in a threadpool since transformers is blocking
            result = await asyncio.to_thread(self.sentiment_pipeline, text)
            top_result = result[0]
            
            raw_label = top_result['label'].upper()
            confidence = float(top_result['score'])

            # THRESHOLD LOGIC:
            # DistilBert only knows POS/NEG. If it's unsure (low score), we force NEUTRAL.
            if confidence < self.neutral_threshold:
                final_label = "neutral"
            else:
                label_map = {
                    "POSITIVE": "positive",
                    "NEGATIVE": "negative",
                    "LABEL_1": "positive", # Support for some model variants
                    "LABEL_0": "negative"
                }
                final_label = label_map.get(raw_label, "neutral")

            return {
                'sentiment_label': final_label,
                'confidence_score': confidence,
                'model_name': self.sentiment_model_name
            }
        
        return {"sentiment_label": "neutral", "confidence_score": 0.0}

    async def analyze_emotion(self, text: str) -> dict:
        """Detect emotion (joy, anger, etc)"""
        if not text:
            raise ValueError("Input text cannot be empty")

        if self.model_type == 'local':
            result = await asyncio.to_thread(self.emotion_pipeline, text)
            top_result = result[0]
            
            return {
                'emotion': top_result['label'],
                'confidence_score': float(top_result['score']),
                'model_name': self.emotion_model_name
            }
            
        return {}

    async def batch_analyze(self, texts: list) -> list:
        if not texts:
            return []
        
        results = []
        for text in texts:
            try:
                res = await self.analyze_sentiment(text)
                results.append(res)
            except Exception as e:
                logger.error(f"Error analyzing text: {e}")
                results.append(None)
        return results