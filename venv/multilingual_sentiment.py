# Import the new sentiment analysis model
from sentiment_model import sentiment_analyzer, aspect_analyzer

# Updated sentiment analysis functions using the new model
def analyze_sentiment(text):
    """
    Advanced sentiment analysis function using multiple methods
    """
    try:
        result = sentiment_analyzer.analyze_sentiment(text)
        return {
            'label': result.label,
            'confidence': result.confidence,
            'scores': result.scores,
            'method': result.method
        }
    except Exception as e:
        # Fallback to basic analysis
        return {'label': 'Neutral', 'confidence': 0.5, 'error': str(e)}

def analyze_aspect_sentiment(text, aspect):
    """
    Advanced aspect-based sentiment analysis function
    """
    try:
        result = aspect_analyzer.analyze_aspect_sentiment(text, aspect)
        return result
    except Exception as e:
        # Fallback response
        return {
            'label': 'Neutral', 
            'confidence': 0.5, 
            'aspect_mentioned': False,
            'error': str(e)
        }
"""
Multilingual sentiment analysis with translation support
"""

# from multilingual_sentiment import analyze_sentiment, analyze_aspect_sentiment
from language_config import language_manager
import streamlit as st
from typing import Dict, Tuple, Optional

class MultilingualSentimentAnalyzer:
    def __init__(self):
        self.language_manager = language_manager
    
    def analyze_multilingual_sentiment(self, text: str, target_lang: str = 'en') -> Dict:
        """
        Analyze sentiment of text, translating if necessary
        """
        # Detect original language
        original_lang = self.language_manager.detect_language(text)
        
        # Translate to English for sentiment analysis if needed
        text_for_analysis = text
        if original_lang != 'en':
            text_for_analysis = self.language_manager.translate_text(
                text, 'en', original_lang
            )
        
        # Perform sentiment analysis
        sentiment_result = analyze_sentiment(text_for_analysis)
        
        # Add language information
        sentiment_result.update({
            'original_language': original_lang,
            'translated_text': text_for_analysis if original_lang != 'en' else None,
            'original_text': text
        })
        
        return sentiment_result
    
    def analyze_multilingual_aspect_sentiment(self, text: str, aspect: str, target_lang: str = 'en') -> Dict:
        """
        Analyze aspect-based sentiment with translation support
        """
        # Detect original language
        original_lang = self.language_manager.detect_language(text)
        
        # Translate to English for analysis if needed
        text_for_analysis = text
        if original_lang != 'en':
            text_for_analysis = self.language_manager.translate_text(
                text, 'en', original_lang
            )
        
        # Perform aspect sentiment analysis
        aspect_result = analyze_aspect_sentiment(text_for_analysis, aspect)
        
        # Add language information
        aspect_result.update({
            'original_language': original_lang,
            'translated_text': text_for_analysis if original_lang != 'en' else None,
            'original_text': text
        })
        
        return aspect_result
    
    def translate_sentiment_label(self, label: str, target_lang: str) -> str:
        """
        Translate sentiment labels to target language
        """
        sentiment_translations = {
            'en': {'Positive': 'Positive', 'Negative': 'Negative', 'Neutral': 'Neutral'},
            'es': {'Positive': 'Positivo', 'Negative': 'Negativo', 'Neutral': 'Neutral'},
            'fr': {'Positive': 'Positif', 'Negative': 'Négatif', 'Neutral': 'Neutre'},
            'de': {'Positive': 'Positiv', 'Negative': 'Negativ', 'Neutral': 'Neutral'},
            'hi': {'Positive': 'सकारात्मक', 'Negative': 'नकारात्मक', 'Neutral': 'तटस्थ'},
            'it': {'Positive': 'Positivo', 'Negative': 'Negativo', 'Neutral': 'Neutrale'},
            'pt': {'Positive': 'Positivo', 'Negative': 'Negativo', 'Neutral': 'Neutro'},
            'ru': {'Positive': 'Положительный', 'Negative': 'Отрицательный', 'Neutral': 'Нейтральный'},
            'ja': {'Positive': 'ポジティブ', 'Negative': 'ネガティブ', 'Neutral': 'ニュートラル'},
            'ko': {'Positive': '긍정적', 'Negative': '부정적', 'Neutral': '중립적'},
            'zh': {'Positive': '积极', 'Negative': '消极', 'Neutral': '中性'},
            'ar': {'Positive': 'إيجابي', 'Negative': 'سلبي', 'Neutral': 'محايد'}
        }
        
        if target_lang in sentiment_translations and label in sentiment_translations[target_lang]:
            return sentiment_translations[target_lang][label]
        
        return label

# Global multilingual sentiment analyzer
multilingual_analyzer = MultilingualSentimentAnalyzer()
