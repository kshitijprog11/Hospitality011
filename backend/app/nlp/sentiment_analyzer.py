from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from textblob import TextBlob
import asyncio
import logging
from typing import Tuple, Dict, Any
from ..core.config import settings

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.sentiment_pipeline = None
        self.fallback_to_textblob = True
        
    async def initialize(self):
        """Initialize the sentiment analysis model"""
        try:
            logger.info("Initializing sentiment analysis model...")
            # Use a more specific sentiment analysis model
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                max_length=512,
                truncation=True,
                return_all_scores=True
            )
            logger.info("Sentiment analysis model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Hugging Face model: {e}")
            logger.info("Falling back to TextBlob for sentiment analysis")
            self.sentiment_pipeline = None
    
    def _normalize_hf_sentiment(self, results: list) -> Tuple[float, str, float]:
        """
        Normalize Hugging Face sentiment results to our scale
        Returns: (sentiment_score, sentiment_label, confidence)
        """
        # Results format: [{'label': 'LABEL_0', 'score': 0.x}, {'label': 'LABEL_1', 'score': 0.y}, ...]
        # LABEL_0 = negative, LABEL_1 = neutral, LABEL_2 = positive
        
        sentiment_map = {
            'LABEL_0': 'negative',
            'LABEL_1': 'neutral', 
            'LABEL_2': 'positive'
        }
        
        # Find the highest scoring sentiment
        best_result = max(results, key=lambda x: x['score'])
        label = sentiment_map.get(best_result['label'], 'neutral')
        confidence = best_result['score']
        
        # Convert to -1 to 1 scale
        if label == 'positive':
            sentiment_score = 0.5 + (confidence - 0.33) * 1.5  # Scale to 0.5 to 1.0
        elif label == 'negative':
            sentiment_score = -0.5 - (confidence - 0.33) * 1.5  # Scale to -1.0 to -0.5
        else:  # neutral
            sentiment_score = (confidence - 0.33) * 0.6  # Scale to -0.2 to 0.2
            
        # Clamp to [-1, 1] range
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        return sentiment_score, label, confidence
    
    def _textblob_sentiment(self, text: str) -> Tuple[float, str, float]:
        """
        Fallback sentiment analysis using TextBlob
        Returns: (sentiment_score, sentiment_label, confidence)
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # Already in -1 to 1 range
        
        # Determine label based on polarity
        if polarity > 0.1:
            label = 'positive'
        elif polarity < -0.1:
            label = 'negative'
        else:
            label = 'neutral'
            
        # Confidence is the absolute value of polarity (how far from neutral)
        confidence = abs(polarity)
        
        return polarity, label, confidence
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        Returns: {
            'sentiment': float,  # -1 to 1 scale
            'sentiment_label': str,  # 'positive', 'negative', 'neutral'
            'confidence': float,  # 0 to 1 confidence score
            'flagged': bool  # True if should be flagged for attention
        }
        """
        try:
            if self.sentiment_pipeline:
                # Use Hugging Face model
                results = self.sentiment_pipeline(text)[0]  # Get first (and only) result
                sentiment_score, sentiment_label, confidence = self._normalize_hf_sentiment(results)
            else:
                # Fallback to TextBlob
                sentiment_score, sentiment_label, confidence = self._textblob_sentiment(text)
            
            # Check if should be flagged
            flagged = self._should_flag(text, sentiment_score, sentiment_label)
            
            return {
                'sentiment': round(sentiment_score, 3),
                'sentiment_label': sentiment_label,
                'confidence': round(confidence, 3),
                'flagged': flagged
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            # Return neutral sentiment on error
            return {
                'sentiment': 0.0,
                'sentiment_label': 'neutral',
                'confidence': 0.0,
                'flagged': False
            }
    
    def _should_flag(self, text: str, sentiment_score: float, sentiment_label: str) -> bool:
        """
        Determine if feedback should be flagged for urgent attention
        """
        # Flag if sentiment is very negative
        if sentiment_score <= settings.alert_threshold_sentiment:
            return True
        
        # Flag if contains urgent keywords
        text_lower = text.lower()
        for keyword in settings.flagged_keywords:
            if keyword.lower() in text_lower:
                return True
                
        return False

# Global sentiment analyzer instance
sentiment_analyzer = SentimentAnalyzer()