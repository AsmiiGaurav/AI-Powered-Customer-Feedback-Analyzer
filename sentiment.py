from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import softmax
import torch

# Load model and tokenizer
model_name = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, use_safetensors=True)

# Label mapping
labels = ['Negative', 'Neutral', 'Positive']

def analyze_sentiment(text):
    # Tokenize input
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    
    # Get logits from model
    with torch.no_grad():
        outputs = model(**inputs)
        scores = softmax(outputs.logits, dim=1)
    
    # Extract highest scoring label
    sentiment_score = scores[0].tolist()
    sentiment_label = labels[sentiment_score.index(max(sentiment_score))]

    return {
        "label": sentiment_label,
        "scores": {
            "Negative": round(sentiment_score[0], 3),
            "Neutral": round(sentiment_score[1], 3),
            "Positive": round(sentiment_score[2], 3)
        }
    }
#testing

if __name__ == "__main__":
    test_review = "The ambience was amazing but the service was too slow."
    result = analyze_sentiment(test_review)
    print("Review:", test_review)
    print("Sentiment Analysis:", result)