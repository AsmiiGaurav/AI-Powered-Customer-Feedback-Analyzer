from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever
from multilingual_sentiment import multilingual_analyzer
from collections import Counter
import re
import warnings
warnings.filterwarnings("ignore", message="Could not load primary model")

# Initialize the model
model = OllamaLLM(model="mistral")

# Enhanced template for natural, user-friendly responses
template = """
You are a restaurant review expert helping customers understand what others think about this restaurant.

Based on customer reviews and sentiment analysis:

CUSTOMER FEEDBACK:
{reviews_with_sentiment}

OVERALL SENTIMENT:
{sentiment_summary}

QUESTION: {question}

Instructions:
- Provide a natural, conversational summary without mentioning "Review 1", "Review 2", etc.
- Synthesize the feedback into clear insights about what customers generally think
- Use phrases like "Customers generally feel...", "Many guests mention...", "The consensus seems to be..."
- Include specific quotes naturally (e.g., "One customer noted that..." or "As one diner put it...")
- Be balanced - mention both strengths and areas for improvement if they exist
- Focus on patterns and trends rather than individual review details
- Make your response helpful for someone deciding whether to visit this restaurant

Provide a helpful, natural summary:"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def get_aspect_from_question(question):
    """
    Determine which aspect the question is about based on keywords
    """
    question_lower = question.lower()
    
    aspect_keywords = {
        'Food': ['food', 'taste', 'flavor', 'dish', 'meal', 'cuisine', 'delicious', 'tasty', 'pizza', 'pasta', 'menu'],
        'Service': ['service', 'staff', 'waiter', 'server', 'friendly', 'helpful', 'rude', 'slow', 'fast', 'attentive'],
        'Ambience': ['ambience', 'atmosphere', 'environment', 'decor', 'music', 'lighting', 'cozy', 'noisy', 'clean'],
        'Price': ['price', 'cost', 'expensive', 'cheap', 'value', 'money', 'worth', 'affordable', 'overpriced','quantity']
    }
    
    for aspect, keywords in aspect_keywords.items():
        if any(keyword in question_lower for keyword in keywords):
            return aspect
    
    return None

def format_reviews_with_sentiment(reviews, question):
    """
    Format reviews with sentiment analysis for the LLM prompt - without review numbers
    """
    review_contents = []
    detected_aspect = get_aspect_from_question(question)
    
    for review in reviews:
        text = review.page_content
        
        # General sentiment analysis
        general_sentiment = multilingual_analyzer.analyze_multilingual_sentiment(text)
        
        # Extract rating from metadata if available
        rating = ""
        if 'rating' in review.metadata:
            rating = f" (Rating: {review.metadata['rating']}/5)"
        
        # Aspect-specific sentiment if relevant
        aspect_info = ""
        if detected_aspect:
            aspect_sentiment = multilingual_analyzer.analyze_multilingual_aspect_sentiment(text, detected_aspect)
            if aspect_sentiment['aspect_mentioned']:
                aspect_info = f" - {detected_aspect} sentiment: {aspect_sentiment['label']}"
        
        # Format without review numbers - just the content and sentiment
        formatted_content = f"Customer feedback: \"{text}\"{rating} - Overall sentiment: {general_sentiment['label']}{aspect_info}"
        review_contents.append(formatted_content)
    
    return "\n\n".join(review_contents)

def create_sentiment_summary(reviews, question):
    """
    Create a summary of sentiment patterns across all reviews
    """
    sentiments = []
    detected_aspect = get_aspect_from_question(question)
    
    # Collect all sentiments
    for review in reviews:
        text = review.page_content
        sentiment = multilingual_analyzer.analyze_multilingual_sentiment(text)
        sentiments.append(sentiment['label'])
    
    # Count sentiment distribution
    sentiment_counts = Counter(sentiments)
    total_reviews = len(sentiments)
    
    summary_parts = []
    summary_parts.append(f"Total reviews analyzed: {total_reviews}")
    
    for sentiment_label in ['Positive', 'Neutral', 'Negative']:
        count = sentiment_counts.get(sentiment_label, 0)
        percentage = (count / total_reviews) * 100 if total_reviews > 0 else 0
        summary_parts.append(f"{sentiment_label}: {count} reviews ({percentage:.1f}%)")
    
    # Add aspect-specific summary if relevant
    if detected_aspect:
        aspect_mentions = 0
        aspect_sentiments = []
        
        for review in reviews:
            text = review.page_content
            aspect_sentiment = multilingual_analyzer.analyze_multilingual_aspect_sentiment(text, detected_aspect)
            if aspect_sentiment['aspect_mentioned']:
                aspect_mentions += 1
                aspect_sentiments.append(aspect_sentiment['label'])
        
        if aspect_mentions > 0:
            aspect_counts = Counter(aspect_sentiments)
            summary_parts.append(f"\n{detected_aspect}-specific mentions: {aspect_mentions} reviews")
            
            for sentiment_label in ['Positive', 'Neutral', 'Negative']:
                count = aspect_counts.get(sentiment_label, 0)
                if count > 0:
                    percentage = (count / aspect_mentions) * 100
                    summary_parts.append(f"  {sentiment_label}: {count} ({percentage:.1f}%)")
    
    return "\n".join(summary_parts)

def display_sentiment_analysis(reviews, question):
    """
    Display detailed sentiment analysis for console output
    """
    print("=" * 60)
    print("SENTIMENT ANALYSIS OF RELEVANT REVIEWS")
    print("=" * 60)
    
    detected_aspect = get_aspect_from_question(question)
    if detected_aspect:
        print(f"🎯 Detected aspect focus: {detected_aspect}")
        print()
    
    for i, review in enumerate(reviews):
        text = review.page_content
        sentiment = multilingual_analyzer.analyze_multilingual_sentiment(text)
        
        # Color coding for console output
        emoji_map = {
            'Positive': '😊',
            'Neutral': '😐',
            'Negative': '😞'
        }
        
        emoji = emoji_map.get(sentiment['label'], '❓')
        
        print(f"Review {i+1}: {emoji} {sentiment['label']} (confidence: {sentiment['confidence']:.3f})")
        print(f"Content: {text[:100]}{'...' if len(text) > 100 else ''}")
        
        # Show aspect-specific sentiment if relevant
        if detected_aspect:
            aspect_sentiment = multilingual_analyzer.analyze_multilingual_aspect_sentiment(text, detected_aspect)
            if aspect_sentiment['aspect_mentioned']:
                aspect_emoji = emoji_map.get(aspect_sentiment['label'], '❓')
                print(f"  └─ {detected_aspect}: {aspect_emoji} {aspect_sentiment['label']} ({aspect_sentiment['confidence']:.3f})")
        
        # Show rating if available
        if 'rating' in review.metadata:
            stars = '⭐' * int(review.metadata['rating'])
            print(f"  └─ Rating: {stars} ({review.metadata['rating']}/5)")
        
        print("-" * 50)

def main():
    """
    Main application loop
    """
    print("🍕 Restaurant Review Analyzer with Sentiment Analysis")
    print("Ask questions about the restaurant based on customer reviews!")
    print("Examples:")
    print("  - 'How is the food quality?'")
    print("  - 'What do customers say about the service?'")
    print("  - 'Is the restaurant good value for money?'")
    print("  - 'How's the atmosphere?'")
    print("\nType 'q' to quit\n")
    
    while True:
        print("\n" + "="*80)
        question = input("❓ Ask your question: ").strip()
        print()
        
        if question.lower() == 'q':
            print("👋 Thanks for using the Restaurant Review Analyzer!")
            break
        
        if not question:
            print("Please enter a valid question.")
            continue
        
        try:
            # Step 1: Get top 5 relevant reviews using semantic search
            print("🔍 Searching for relevant reviews...")
            reviews = retriever.invoke(question)
            
            if not reviews:
                print("❌ No relevant reviews found for your question.")
                continue
            
            # Step 2: Display detailed sentiment analysis
            display_sentiment_analysis(reviews, question)
            
            # Step 3: Prepare data for LLM
            print("\n🤖 Generating comprehensive answer...")
            reviews_with_sentiment = format_reviews_with_sentiment(reviews, question)
            sentiment_summary = create_sentiment_summary(reviews, question)
            
            # Step 4: Get LLM response
            result = chain.invoke({
                "reviews_with_sentiment": reviews_with_sentiment,
                "sentiment_summary": sentiment_summary,
                "question": question
            })
            
            # Step 5: Display final answer
            print("\n" + "="*60)
            print("🎯 AI ANALYSIS")
            print("="*60)
            print(result)
            
        except Exception as e:
            print(f"❌ An error occurred: {str(e)}")
            print("Please try again with a different question.")

if __name__ == "__main__":
    main()