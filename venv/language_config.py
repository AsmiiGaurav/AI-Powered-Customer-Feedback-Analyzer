"""
Language configuration and translation utilities for multilingual support
"""

import json
import os
from typing import Dict, List, Optional
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
import streamlit as st

# Set seed for consistent language detection
DetectorFactory.seed = 0

class LanguageManager:
    def __init__(self):
        self.deep_translator = GoogleTranslator
        self.supported_languages = {
            'en': {'name': 'English', 'flag': '🇺🇸'},
            'es': {'name': 'Español', 'flag': '🇪🇸'},
            'fr': {'name': 'Français', 'flag': '🇫🇷'},
            'de': {'name': 'Deutsch', 'flag': '🇩🇪'},
            'it': {'name': 'Italiano', 'flag': '🇮🇹'},
            'pt': {'name': 'Português', 'flag': '🇵🇹'},
            'ru': {'name': 'Русский', 'flag': '🇷🇺'},
            'ja': {'name': '日本語', 'flag': '🇯🇵'},
            'ko': {'name': '한국어', 'flag': '🇰🇷'},
            'zh': {'name': '中文', 'flag': '🇨🇳'},
            'ar': {'name': 'العربية', 'flag': '🇸🇦'},
            'hi': {'name': 'हिन्दी', 'flag': '🇮🇳'},
            'nl': {'name': 'Nederlands', 'flag': '🇳🇱'},
            'sv': {'name': 'Svenska', 'flag': '🇸🇪'},
            'da': {'name': 'Dansk', 'flag': '🇩🇰'},
            'no': {'name': 'Norsk', 'flag': '🇳🇴'},
            'fi': {'name': 'Suomi', 'flag': '🇫🇮'},
            'pl': {'name': 'Polski', 'flag': '🇵🇱'},
            'tr': {'name': 'Türkçe', 'flag': '🇹🇷'},
            'th': {'name': 'ไทย', 'flag': '🇹🇭'}
        }
        
        # Load translations
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict:
        """Load UI translations from JSON file"""
        translations_file = os.path.join(os.path.dirname(__file__), 'translations.json')
        if os.path.exists(translations_file):
            with open(translations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def detect_language(self, text: str) -> str:
        """Detect the language of given text"""
        try:
            detected = detect(text)
            return detected if detected in self.supported_languages else 'en'
        except:
            return 'en'
    
    def translate_text(self, text: str, target_lang: str, source_lang: str = 'auto') -> str:
        """Translate text to target language"""
        if not text or target_lang == source_lang:
            return text
        
        try:
            # Use deep-translator
            translator = self.deep_translator(source=source_lang, target=target_lang)
            result = translator.translate(text)
            return result
        except Exception as e:
            st.warning(f"Translation failed: {str(e)}")
            return text
    
    def get_ui_text(self, key: str, lang: str = 'en') -> str:
        """Get UI text in specified language"""
        if lang in self.translations and key in self.translations[lang]:
            return self.translations[lang][key]
        elif key in self.translations.get('en', {}):
            return self.translations['en'][key]
        else:
            return key.replace('_', ' ').title()
    
    def get_language_options(self) -> Dict[str, str]:
        """Get formatted language options for UI"""
        return {
            code: f"{info['flag']} {info['name']}"
            for code, info in self.supported_languages.items()
        }
    
    def is_rtl_language(self, lang_code: str) -> bool:
        """Check if language is right-to-left"""
        rtl_languages = ['ar', 'he', 'fa', 'ur']
        return lang_code in rtl_languages

# Global language manager instance
language_manager = LanguageManager()
