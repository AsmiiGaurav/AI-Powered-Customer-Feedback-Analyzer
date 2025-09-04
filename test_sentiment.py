"""
Test script for the sentiment analysis model
"""

import sys
import os

# Add venv folder to Python path
venv_path = os.path.join(os.path.dirname(__file__), 'venv')
if venv_path not in sys.path:
    sys.path.append(venv_path)

def test_sentiment_analysis():
    """Test the sentiment analysis functionality"""
    print("🧪 Testing Sentiment Analysis Model")
    print("=" * 50)
    
    try:
        from sentiment_model import sentiment_analyzer, aspect_analyzer
        from multilingual_sentiment import multilingual_analyzer
        
        # Test cases
        test_reviews = [
            {
                'text': "The food was absolutely delicious and the service was excellent!",
                'expected': 'Positive'
            },
            {
                'text': "Terrible food, slow service, and overpriced. Never going back!",
                'expected': 'Negative'
            },
            {
                'text': "The restaurant was okay. Nothing special but not bad either.",
                'expected': 'Neutral'
            },
            {
                'text': "Amazing pasta and great atmosphere, but the service was a bit slow.",
                'expected': 'Positive'  # Mixed but overall positive
            }
        ]
        
        print("1. Testing Basic Sentiment Analysis:")
        print("-" * 30)
        
        for i, review in enumerate(test_reviews, 1):
            result = sentiment_analyzer.analyze_sentiment(review['text'])
            print(f"Review {i}: {review['text'][:50]}...")
            print(f"Expected: {review['expected']}")
            print(f"Predicted: {result.label} (Confidence: {result.confidence:.3f})")
            print(f"Method: {result.method}")
            print(f"Scores: {result.scores}")
            print()
        
        print("2. Testing Aspect-Based Sentiment Analysis:")
        print("-" * 40)
        
        aspect_test = "The food was amazing and delicious, but the service was terrible and slow. The atmosphere was cozy though."
        aspects = ['food', 'service', 'ambience']
        
        print(f"Review: {aspect_test}")
        print()
        
        for aspect in aspects:
            result = aspect_analyzer.analyze_aspect_sentiment(aspect_test, aspect)
            print(f"{aspect.capitalize()} Aspect:")
            print(f"  Sentiment: {result['label']} (Confidence: {result['confidence']:.3f})")
            print(f"  Mentioned: {result['aspect_mentioned']}")
            if result['aspect_mentioned'] and 'aspect_sentences' in result:
                print(f"  Sentences: {result['aspect_sentences']}")
            print()
        
        print("3. Testing Multilingual Analysis:")
        print("-" * 30)
        
        multilingual_tests = [
            "The food was excellent!",  # English
            "La comida estaba excelente!",  # Spanish
            "Das Essen war ausgezeichnet!",  # German
        ]
        
        for text in multilingual_tests:
            result = multilingual_analyzer.analyze_multilingual_sentiment(text)
            print(f"Text: {text}")
            print(f"Language: {result.get('original_language', 'unknown')}")
            print(f"Sentiment: {result['label']} (Confidence: {result['confidence']:.3f})")
            if result.get('translated_text'):
                print(f"Translated: {result['translated_text']}")
            print()
        
        print("✅ All tests completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Some dependencies might not be installed. The model will use fallback methods.")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def test_installation():
    """Test if required packages are available"""
    print("🔍 Checking Package Installation:")
    print("-" * 30)
    
    packages = [
        ('vaderSentiment', 'VADER Sentiment'),
        ('textblob', 'TextBlob'),
        ('transformers', 'Transformers'),
        ('torch', 'PyTorch'),
        ('numpy', 'NumPy'),
        ('langdetect', 'Language Detection'),
    ]
    
    available = []
    missing = []
    
    for package, name in packages:
        try:
            __import__(package)
            print(f"✅ {name}: Available")
            available.append(package)
        except ImportError:
            print(f"❌ {name}: Not installed")
            missing.append(package)
    
    print(f"\nSummary: {len(available)}/{len(packages)} packages available")
    
    if missing:
        print(f"\nTo install missing packages, run:")
        print(f"pip install {' '.join(missing)}")
    
    return len(missing) == 0

if __name__ == "__main__":
    print("🚀 Sentiment Analysis Model Test Suite")
    print("=" * 50)
    
    # Test installation
    installation_ok = test_installation()
    print()
    
    # Test functionality
    if installation_ok:
        test_sentiment_analysis()
    else:
        print("⚠️  Some packages are missing, but the model should still work with fallback methods.")
        test_sentiment_analysis()
