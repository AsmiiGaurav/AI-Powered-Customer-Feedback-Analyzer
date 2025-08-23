import streamlit as st
import sys
import os

# Add venv folder to Python path
venv_path = os.path.join(os.path.dirname(__file__), 'venv')
if venv_path not in sys.path:
    sys.path.append(venv_path)

from main import chain
from vector import retriever
from sentiment import analyze_sentiment, analyze_aspect_sentiment

# Set page configuration
st.set_page_config(page_title="Restaurant Review Analysis", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
        .main {
            background-image: url('https://images.unsplash.com/photo-1495195134817-aeb325a55b65?ixlib=rb-4.0.3');
            background-size: cover;
        }
        .stApp {
            background: rgba(255, 255, 255, 0.92);
        }
        .css-1d391kg {
            padding: 2rem 1rem;
        }
        /* Make chat messages dark and readable */
        .stChatMessage {
            color: #1a1a1a !important;
        }
        [data-testid="stChatMessageContent"] {
            background-color: #f0f2f6 !important;
            color: #1a1a1a !important;
        }
        /* Style dashboard/sidebar text */
        [data-testid="stSidebar"] {
            background-color: rgba(0, 0, 0, 0.8) !important;
            color: white !important;
        }
        [data-testid="stSidebar"] .stMarkdown {
            color: white !important;
        }
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] ul,
        [data-testid="stSidebar"] li {
            color: white !important;
        }
        /* Keep main content area text dark */
        .element-container .stMarkdown {
            color: #1a1a1a !important;
        }
        /* Style chat input */
        .stChatInputContainer {
            background-color: white !important;
        }
        .stButton>button {
            background-color: #ff4b4b;
            color: white;
            border-radius: 20px;
            padding: 0.5rem 1rem;
            border: none;
        }
        .stButton>button:hover {
            background-color: #ff2b2b;
        }
        div[data-testid="stExpander"] {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            border: 1px solid #ff4b4b;
            padding: 10px;
        }
        .sentiment-positive {
            color: #28a745;
            font-weight: bold;
        }
        .sentiment-negative {
            color: #dc3545;
            font-weight: bold;
        }
        .sentiment-neutral {
            color: #6c757d;
            font-weight: bold;
        }
        .review-card {
            background-color: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

# Custom function to format sentiment
def format_sentiment(label, confidence):
    color_class = f"sentiment-{label.lower()}"
    return f'<span class="{color_class}">{label} ({confidence:.2f})</span>'
# Header section with emojis and styled title
st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <h1 style='color: #ff4b4b; margin-bottom: 0;'>🍕 Restaurant Review Analysis 🍽️</h1>
        <p style='font-style: italic; color: #666;'>Ask anything about our restaurant reviews!</p>
    </div>
    """, unsafe_allow_html=True)

# Initialize session state for chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

    # Sidebar styling and content
with st.sidebar:
    st.markdown("""
        <div style='text-align: center;'>
            <h2 style='color: white;'>📊 Dashboard</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Add some tips for users with white text
    st.markdown("### 💡 Example Questions")
    st.markdown("""
        - "How's the pizza quality?"
        - "What's the service like?"
        - "Is it good value for money?"
        - "Tell me about the atmosphere"
    """)
    
    st.markdown("### 🏷️ Key Features")
    st.markdown("""
        - Real-time sentiment analysis
        - Aspect-based insights
        - Review summarization
    """)
    
    # Add a subtle separator
    st.markdown("<hr style='border-color: rgba(255,255,255,0.2);'>", unsafe_allow_html=True)# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about the restaurant reviews"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get relevant reviews
    reviews = retriever.invoke(prompt)
    
    # Display response
    with st.chat_message("assistant"):
        # Show reviews being analyzed
        with st.expander("Relevant Reviews"):
            for i, review in enumerate(reviews, 1):
                text = review.page_content
                sentiment = analyze_sentiment(text)
                
                # Create a card-like container for each review
                st.markdown(f"""
                    <div class='review-card'>
                        <h4 style='color: #ff4b4b; margin: 0;'>Review #{i}</h4>
                        <p style='margin: 0.5rem 0;'>{text}</p>
                        <p>Overall Sentiment: {format_sentiment(sentiment['label'], sentiment['confidence'])}</p>
                    """, unsafe_allow_html=True)
                
                # If aspect-specific question, show aspect sentiment
                aspect = None
                for key in ['food', 'service', 'ambience', 'price']:
                    if key in prompt.lower():
                        aspect = key.capitalize()
                        aspect_sentiment = analyze_aspect_sentiment(text, aspect)
                        if aspect_sentiment['aspect_mentioned']:
                            st.markdown(
                                f"<p>{aspect} Sentiment: "
                                f"{format_sentiment(aspect_sentiment['label'], aspect_sentiment['confidence'])}</p>",
                                unsafe_allow_html=True
                            )
                
                # Add any metadata (like rating) if available
                if hasattr(review, 'metadata') and 'rating' in review.metadata:
                    rating = review.metadata['rating']
                    stars = '⭐' * int(rating)
                    st.markdown(f"<p>Rating: {stars} ({rating}/5)</p>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)

        # Generate and display AI response
        with st.spinner("Analyzing reviews..."):
            reviews_with_sentiment = []
            sentiment_summary = []
            
            # Format reviews with sentiment
            for review in reviews:
                text = review.page_content
                sentiment = analyze_sentiment(text)
                reviews_with_sentiment.append(f"{text} - {sentiment['label']}")
            
            # Get AI response
            response = chain.invoke({
                "reviews_with_sentiment": "\n".join(reviews_with_sentiment),
                "sentiment_summary": "\n".join(sentiment_summary),
                "question": prompt
            })
            
            # Add response to chat history
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": str(response)})

# Sidebar with options
with st.sidebar:
    st.header("Options")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
