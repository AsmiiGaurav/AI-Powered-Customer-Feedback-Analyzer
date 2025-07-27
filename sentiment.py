from transformers import pipeline
import torch

# Check if CUDA is available for faster inference
device = 0 if torch.cuda.is_available() else -1

# Initialize the sentiment analysis pipeline
# Using a model specifically fine-tuned for sentiment analysis
try:
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="cardiffnlp/twitter-roberta-base-sentiment-latest",
        device=device
    )
except Exception as e:
    print(f"Warning: Could not load primary model, falling back to default: {e}")
    # Fallback to a simpler model if the above fails
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=device
    )

def map_label_to_standard(label, score):
    """
    Map different model outputs to standard labels: Negative, Neutral, Positive
    """
    label = label.upper()
    
    # Handle different model label formats
    if label in ['NEGATIVE', 'NEG']:
        return 'Negative'
    elif label in ['POSITIVE', 'POS']:
        return 'Positive'
    elif label in ['NEUTRAL', 'NEU']:
        return 'Neutral'
    elif label == 'LABEL_0':  # Some models use LABEL_0 for negative
        return 'Negative'
    elif label == 'LABEL_1':  # Some models use LABEL_1 for positive
        return 'Positive'
    else:
        # If score-based mapping is needed (for models without neutral)
        if score >= 0.6:
            return 'Positive' if label in ['POSITIVE', 'LABEL_1'] else 'Negative'
        elif score <= 0.4:
            return 'Negative' if label in ['NEGATIVE', 'LABEL_0'] else 'Positive'
        else:
            return 'Neutral'

def analyze_sentiment(text):
    """
    Analyze sentiment of given text and return standardized result
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Contains 'label' (Negative/Neutral/Positive) and 'confidence' (float)
    """
    if not text or not isinstance(text, str):
        return {'label': 'Neutral', 'confidence': 0.0}
    
    # Clean the text (remove extra whitespace, handle empty strings)
    text = text.strip()
    if len(text) == 0:
        return {'label': 'Neutral', 'confidence': 0.0}
    
    try:
        # Get prediction from the model
        result = sentiment_pipeline(text)[0]
        
        # Extract label and confidence
        raw_label = result['label']
        confidence = result['score']
        
        # Map to standard labels
        standard_label = map_label_to_standard(raw_label, confidence)
        
        return {
            'label': standard_label,
            'confidence': round(confidence, 3)
        }
        
    except Exception as e:
        print(f"Error analyzing sentiment for text: '{text[:50]}...': {e}")
        return {'label': 'Neutral', 'confidence': 0.0}

def analyze_aspect_sentiment(text, aspect):
    """
    Analyze sentiment for a specific aspect (e.g., Food, Service, Ambience, Price)
    
    Args:
        text (str): Review text
        aspect (str): Aspect to focus on (Food, Service, Ambience, Price)
        
    Returns:
        dict: Contains 'label', 'confidence', and 'aspect'
    """
    # Create aspect-focused prompt
    aspect_keywords = {
        'Food': ['food', 'taste', 'flavor', 'dish', 'meal', 'cuisine', 'delicious', 'tasty'],
        'Service': ['service', 'staff', 'waiter', 'server', 'friendly', 'helpful', 'rude'],
        'Ambience': ['ambience', 'atmosphere', 'environment', 'decor', 'music', 'lighting', 'cozy'],
        'Price': ['price', 'cost', 'expensive', 'cheap', 'value', 'money', 'worth', 'affordable']
    }
    
    # Check if aspect-related keywords exist in the text
    keywords = aspect_keywords.get(aspect, [])
    text_lower = text.lower()
    
    aspect_mentioned = any(keyword in text_lower for keyword in keywords)
    
    if not aspect_mentioned:
        return {
            'label': 'Neutral',
            'confidence': 0.0,
            'aspect': aspect,
            'aspect_mentioned': False
        }
    
    # Analyze sentiment of the full text (aspect-specific analysis would need more complex NLP)
    sentiment_result = analyze_sentiment(text)
    
    return {
        'label': sentiment_result['label'],
        'confidence': sentiment_result['confidence'],
        'aspect': aspect,
        'aspect_mentioned': True
    }

def batch_analyze_sentiment(texts):
    """
    Analyze sentiment for multiple texts at once (more efficient)
    
    Args:
        texts (list): List of texts to analyze
        
    Returns:
        list: List of sentiment results
    """
    if not texts:
        return []
    
    results = []
    for text in texts:
        results.append(analyze_sentiment(text))
    
    return results

# Example usage and testing
# if __name__ == "__main__":
#     # Test cases
#     test_reviews = [
#         "The food was absolutely amazing and the service was great!",
#         "Terrible experience, food was cold and staff was rude.",
#         "It was okay, nothing special but not bad either.",
#         "Love this place! Best pizza in town and great atmosphere.",
#         "Overpriced for what you get, but the ambience is nice."
#     ]
    
#     print("Testing Sentiment Analysis:")
#     print("-" * 50)
    
#     for i, review in enumerate(test_reviews, 1):
#         result = analyze_sentiment(review)
#         print(f"Review {i}: {result['label']} ({result['confidence']:.3f})")
#         print(f"Text: {review}")
#         print()
    
#     # Test aspect-based sentiment
#     print("\nTesting Aspect-Based Sentiment Analysis:")
#     print("-" * 50)
    
#     sample_review = "The food was delicious but the service was slow and the prices are too high."
#     aspects = ['Food', 'Service', 'Price', 'Ambience']
    
#     for aspect in aspects:
#         result = analyze_aspect_sentiment(sample_review, aspect)
#         if result['aspect_mentioned']:
#             print(f"{aspect}: {result['label']} ({result['confidence']:.3f})")
#         else:
#             print(f"{aspect}: Not mentioned")
