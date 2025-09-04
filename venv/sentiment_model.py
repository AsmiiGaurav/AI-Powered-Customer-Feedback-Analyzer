"""
Advanced Sentiment Analysis Model for Restaurant Reviews
Supports multiple approaches: VADER, TextBlob, and Transformer-based models
"""

import os
import logging
from typing import Dict, List, Tuple, Optional, Union
import numpy as np
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SentimentResult:
    """Data class for sentiment analysis results"""
    label: str
    confidence: float
    scores: Dict[str, float]
    method: str
    original_text: str
    processed_text: Optional[str] = None

class SentimentAnalyzer:
    """
    Multi-method sentiment analysis with fallback options
    """
    
    def __init__(self, preferred_method: str = "hybrid"):
        """
        Initialize sentiment analyzer
        
        Args:
            preferred_method: "vader", "textblob", "transformer", or "hybrid"
        """
        self.preferred_method = preferred_method
        self.available_methods = []
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available sentiment analysis models"""
        
        # Initialize VADER
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.vader_analyzer = SentimentIntensityAnalyzer()
            self.available_methods.append("vader")
            logger.info("✅ VADER sentiment analyzer initialized")
        except ImportError:
            logger.warning("❌ VADER not available")
            self.vader_analyzer = None
        
        # Initialize TextBlob
        try:
            from textblob import TextBlob
            self.textblob_available = True
            self.available_methods.append("textblob")
            logger.info("✅ TextBlob sentiment analyzer initialized")
        except ImportError:
            logger.warning("❌ TextBlob not available")
            self.textblob_available = False
        
        # Initialize Transformer model
        try:
            from transformers import pipeline
            self.transformer_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            self.available_methods.append("transformer")
            logger.info("✅ Transformer sentiment analyzer initialized")
        except Exception as e:
            logger.warning(f"❌ Transformer model not available: {e}")
            self.transformer_analyzer = None
        
        # Fallback to basic rule-based if nothing else works
        if not self.available_methods:
            self.available_methods.append("basic")
            logger.info("✅ Basic rule-based analyzer as fallback")
    
    def _analyze_vader(self, text: str) -> SentimentResult:
        """Analyze sentiment using VADER"""
        if not self.vader_analyzer:
            raise ValueError("VADER analyzer not available")
        
        scores = self.vader_analyzer.polarity_scores(text)
        compound = scores['compound']
        
        # Determine label based on compound score
        if compound >= 0.05:
            label = "Positive"
        elif compound <= -0.05:
            label = "Negative"
        else:
            label = "Neutral"
        
        # Convert compound score to confidence (0-1 range)
        confidence = abs(compound)
        
        return SentimentResult(
            label=label,
            confidence=confidence,
            scores={
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'compound': compound
            },
            method="vader",
            original_text=text
        )
    
    def _analyze_textblob(self, text: str) -> SentimentResult:
        """Analyze sentiment using TextBlob"""
        if not self.textblob_available:
            raise ValueError("TextBlob not available")
        
        from textblob import TextBlob
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Determine label based on polarity
        if polarity > 0.1:
            label = "Positive"
        elif polarity < -0.1:
            label = "Negative"
        else:
            label = "Neutral"
        
        # Use absolute polarity as confidence
        confidence = abs(polarity)
        
        return SentimentResult(
            label=label,
            confidence=confidence,
            scores={
                'polarity': polarity,
                'subjectivity': subjectivity,
                'positive': max(0, polarity),
                'negative': max(0, -polarity),
                'neutral': 1 - abs(polarity)
            },
            method="textblob",
            original_text=text
        )
    
    def _analyze_transformer(self, text: str) -> SentimentResult:
        """Analyze sentiment using transformer model"""
        if not self.transformer_analyzer:
            raise ValueError("Transformer analyzer not available")
        
        # Truncate text if too long (transformer models have token limits)
        max_length = 512
        if len(text) > max_length:
            text = text[:max_length]
        
        results = self.transformer_analyzer(text)[0]
        
        # Convert results to our format
        scores_dict = {}
        max_score = 0
        predicted_label = "Neutral"
        
        for result in results:
            label_map = {
                'LABEL_0': 'Negative',
                'LABEL_1': 'Neutral', 
                'LABEL_2': 'Positive'
            }
            
            label = label_map.get(result['label'], result['label'])
            score = result['score']
            scores_dict[label.lower()] = score
            
            if score > max_score:
                max_score = score
                predicted_label = label
        
        return SentimentResult(
            label=predicted_label,
            confidence=max_score,
            scores=scores_dict,
            method="transformer",
            original_text=text,
            processed_text=text if len(text) < len(text) else None
        )
    
    def _analyze_basic(self, text: str) -> SentimentResult:
        """Basic rule-based sentiment analysis as fallback"""
        text_lower = text.lower()
        
        # Simple positive/negative word lists
        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'delicious', 'tasty', 'fresh', 'perfect', 'love', 'best',
            'outstanding', 'superb', 'brilliant', 'awesome', 'incredible'
        ]
        
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'worst',
            'hate', 'disappointing', 'poor', 'bland', 'cold', 'stale',
            'overpriced', 'slow', 'rude', 'dirty', 'unacceptable'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        
        if positive_count > negative_count:
            label = "Positive"
            confidence = min(0.8, positive_count / max(total_words * 0.1, 1))
        elif negative_count > positive_count:
            label = "Negative"
            confidence = min(0.8, negative_count / max(total_words * 0.1, 1))
        else:
            label = "Neutral"
            confidence = 0.5
        
        return SentimentResult(
            label=label,
            confidence=confidence,
            scores={
                'positive': positive_count / max(total_words, 1),
                'negative': negative_count / max(total_words, 1),
                'neutral': 1 - (positive_count + negative_count) / max(total_words, 1)
            },
            method="basic",
            original_text=text
        )
    
    def analyze_sentiment(self, text: str, method: Optional[str] = None) -> SentimentResult:
        """
        Analyze sentiment of text using specified or preferred method
        
        Args:
            text: Text to analyze
            method: Specific method to use, or None for preferred/hybrid
            
        Returns:
            SentimentResult object
        """
        if not text or not text.strip():
            return SentimentResult(
                label="Neutral",
                confidence=0.0,
                scores={'neutral': 1.0},
                method="empty",
                original_text=text
            )
        
        text = text.strip()
        
        # Determine which method to use
        if method and method in self.available_methods:
            target_method = method
        elif self.preferred_method == "hybrid":
            target_method = "hybrid"
        elif self.preferred_method in self.available_methods:
            target_method = self.preferred_method
        else:
            target_method = self.available_methods[0] if self.available_methods else "basic"
        
        try:
            if target_method == "hybrid":
                return self._analyze_hybrid(text)
            elif target_method == "vader":
                return self._analyze_vader(text)
            elif target_method == "textblob":
                return self._analyze_textblob(text)
            elif target_method == "transformer":
                return self._analyze_transformer(text)
            else:
                return self._analyze_basic(text)
                
        except Exception as e:
            logger.error(f"Error in sentiment analysis with {target_method}: {e}")
            # Fallback to basic method
            return self._analyze_basic(text)
    
    def _analyze_hybrid(self, text: str) -> SentimentResult:
        """
        Hybrid approach combining multiple methods for better accuracy
        """
        results = []
        weights = {"vader": 0.4, "textblob": 0.3, "transformer": 0.3}
        
        # Collect results from available methods
        for method in ["vader", "textblob", "transformer"]:
            if method in self.available_methods:
                try:
                    if method == "vader":
                        result = self._analyze_vader(text)
                    elif method == "textblob":
                        result = self._analyze_textblob(text)
                    elif method == "transformer":
                        result = self._analyze_transformer(text)
                    
                    results.append((result, weights.get(method, 0.33)))
                except Exception as e:
                    logger.warning(f"Method {method} failed: {e}")
        
        if not results:
            return self._analyze_basic(text)
        
        # Weighted voting
        label_scores = {"Positive": 0, "Negative": 0, "Neutral": 0}
        confidence_sum = 0
        total_weight = 0
        
        for result, weight in results:
            label_scores[result.label] += weight * result.confidence
            confidence_sum += weight * result.confidence
            total_weight += weight
        
        # Determine final label
        final_label = max(label_scores, key=label_scores.get)
        final_confidence = confidence_sum / total_weight if total_weight > 0 else 0.5
        
        # Combine scores
        combined_scores = {}
        for result, weight in results:
            for score_name, score_value in result.scores.items():
                if score_name not in combined_scores:
                    combined_scores[score_name] = 0
                combined_scores[score_name] += weight * score_value
        
        # Normalize combined scores
        for score_name in combined_scores:
            combined_scores[score_name] /= total_weight
        
        return SentimentResult(
            label=final_label,
            confidence=final_confidence,
            scores=combined_scores,
            method="hybrid",
            original_text=text
        )

class AspectSentimentAnalyzer:
    """
    Aspect-based sentiment analysis for restaurant reviews
    """
    
    def __init__(self, sentiment_analyzer: SentimentAnalyzer):
        self.sentiment_analyzer = sentiment_analyzer
        
        # Define aspect keywords
        self.aspect_keywords = {
            'food': ['food', 'dish', 'meal', 'taste', 'flavor', 'cuisine', 'recipe', 
                    'ingredient', 'delicious', 'tasty', 'bland', 'spicy', 'sweet'],
            'service': ['service', 'staff', 'waiter', 'waitress', 'server', 'employee',
                       'friendly', 'rude', 'helpful', 'slow', 'fast', 'attentive'],
            'ambience': ['ambience', 'atmosphere', 'environment', 'decor', 'music',
                        'lighting', 'noise', 'cozy', 'romantic', 'loud', 'quiet'],
            'price': ['price', 'cost', 'expensive', 'cheap', 'value', 'money',
                     'affordable', 'overpriced', 'reasonable', 'worth']
        }
    
    def extract_aspect_sentences(self, text: str, aspect: str) -> List[str]:
        """Extract sentences that mention the specified aspect"""
        aspect = aspect.lower()
        keywords = self.aspect_keywords.get(aspect, [aspect])
        
        sentences = text.split('.')
        aspect_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and any(keyword in sentence.lower() for keyword in keywords):
                aspect_sentences.append(sentence)
        
        return aspect_sentences
    
    def analyze_aspect_sentiment(self, text: str, aspect: str) -> Dict:
        """
        Analyze sentiment for a specific aspect
        
        Args:
            text: Review text
            aspect: Aspect to analyze (food, service, ambience, price)
            
        Returns:
            Dictionary with sentiment analysis results
        """
        aspect_sentences = self.extract_aspect_sentences(text, aspect)
        
        if not aspect_sentences:
            return {
                'label': 'Neutral',
                'confidence': 0.0,
                'aspect_mentioned': False,
                'aspect_sentences': [],
                'method': 'not_found'
            }
        
        # Analyze sentiment of aspect-specific sentences
        if len(aspect_sentences) == 1:
            result = self.sentiment_analyzer.analyze_sentiment(aspect_sentences[0])
        else:
            # Combine multiple sentences
            combined_text = '. '.join(aspect_sentences)
            result = self.sentiment_analyzer.analyze_sentiment(combined_text)
        
        return {
            'label': result.label,
            'confidence': result.confidence,
            'aspect_mentioned': True,
            'aspect_sentences': aspect_sentences,
            'scores': result.scores,
            'method': result.method
        }

# Global instances
sentiment_analyzer = SentimentAnalyzer(preferred_method="hybrid")
aspect_analyzer = AspectSentimentAnalyzer(sentiment_analyzer)

# Legacy functions for backward compatibility
def analyze_sentiment(text: str) -> Dict:
    """Legacy function for backward compatibility"""
    result = sentiment_analyzer.analyze_sentiment(text)
    return {
        'label': result.label,
        'confidence': result.confidence,
        'scores': result.scores
    }

def analyze_aspect_sentiment(text: str, aspect: str) -> Dict:
    """Legacy function for backward compatibility"""
    return aspect_analyzer.analyze_aspect_sentiment(text, aspect)
