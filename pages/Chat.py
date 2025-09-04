import streamlit as st
import sys
import os

# Add venv folder to Python path at the beginning to prioritize local modules
venv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'venv'))
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

# Try to import required modules with error handling
try:
    
    # Now try to import normally
    from main import chain
    from vector import retriever
    from multilingual_sentiment import multilingual_analyzer
    
    # Check if components are properly loaded
    if chain is None or retriever is None or multilingual_analyzer is None:
        raise ImportError("One or more components failed to load properly")
    
    IMPORTS_AVAILABLE = True
    print("✅ Successfully imported RAG components in Chat.py")
    
except Exception as e:
    print(f"❌ Import error in Chat.py: {str(e)}")
    IMPORTS_AVAILABLE = False
    # Create mock objects for testing
    class MockAnalyzer:
        def analyze_multilingual_sentiment(self, text):
            return {'label': 'neutral', 'confidence': 0.5, 'original_language': 'en'}
        def analyze_multilingual_aspect_sentiment(self, text, aspect):
            return {'label': 'neutral', 'confidence': 0.5, 'aspect_mentioned': True}
        def translate_sentiment_label(self, label, target_lang):
            return label.title()
    
    multilingual_analyzer = MockAnalyzer()
    chain = None
    retriever = None

def show_page(current_lang, language_manager):
    """Display the Chat page content"""
    
    # Initialize session state for chat
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Custom function to format sentiment with translation
    def format_sentiment_multilingual(label, confidence, target_lang):
        translated_label = multilingual_analyzer.translate_sentiment_label(label, target_lang)
        color_class = f"sentiment-{label.lower()}"
        return f'<span class="{color_class}">{translated_label} ({confidence:.2f})</span>'
    
    # Header section with multilingual support
    st.markdown(f"""
        <div style='text-align: center; padding: 1rem;'>
            <h1 style='color: #ff4b4b; margin-bottom: 0;'>💬 Chat Analysis</h1>
            <p style='font-style: italic; color: #666;'>Ask questions about restaurant reviews and get AI-powered insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Show import status
    if IMPORTS_AVAILABLE:
        st.success("✅ AI analysis features loaded successfully!")
    else:
        st.warning("⚠️ AI analysis features are not available. Running in demo mode.")
    
    # Example questions in selected language
    with st.expander("💡 Example Questions", expanded=False):
        example_questions_text = language_manager.get_ui_text('example_questions', current_lang)
        st.markdown(f"### {example_questions_text}")
        
        food_quality = language_manager.get_ui_text('food_quality', current_lang)
        service_quality = language_manager.get_ui_text('service_quality', current_lang)
        value_money = language_manager.get_ui_text('value_money', current_lang)
        atmosphere = language_manager.get_ui_text('atmosphere', current_lang)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                - "{food_quality}"
                - "{service_quality}"
            """)
        with col2:
            st.markdown(f"""
                - "{value_money}"
                - "{atmosphere}"
            """)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input with multilingual placeholder
    ask_placeholder = language_manager.get_ui_text('ask_placeholder', current_lang)
    if prompt := st.chat_input(ask_placeholder):
        # Detect input language and translate if necessary
        input_lang = language_manager.detect_language(prompt)
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            # Show original message with language detection
            if input_lang != 'en':
                lang_name = language_manager.supported_languages.get(input_lang, {}).get('name', input_lang)
                st.markdown(f"{prompt} <span class='language-badge'>{lang_name}</span>", unsafe_allow_html=True)
            else:
                st.markdown(prompt)

        # Translate question to English for processing if needed
        prompt_for_processing = prompt
        if input_lang != 'en':
            prompt_for_processing = language_manager.translate_text(prompt, 'en', input_lang)

        # Get relevant reviews
        if not IMPORTS_AVAILABLE or retriever is None:
            with st.chat_message("assistant"):
                st.markdown("I'm sorry, but the AI analysis features are currently unavailable. This appears to be a demo mode.")
                st.session_state.messages.append({"role": "assistant", "content": "AI analysis features are currently unavailable in demo mode."})
            return
            
        reviews = retriever.invoke(prompt_for_processing)
        
        # Display response
        with st.chat_message("assistant"):
            if not reviews:
                no_reviews_text = language_manager.get_ui_text('no_reviews_found', current_lang)
                st.markdown(no_reviews_text)
            else:
                # Show reviews being analyzed
                relevant_reviews_text = language_manager.get_ui_text('relevant_reviews', current_lang)
                with st.expander(relevant_reviews_text):
                    for i, review in enumerate(reviews, 1):
                        text = review.page_content
                        
                        # Use multilingual sentiment analysis
                        sentiment = multilingual_analyzer.analyze_multilingual_sentiment(text)
                        
                        # Create a card-like container for each review
                        review_number_text = language_manager.get_ui_text('review_number', current_lang)
                        overall_sentiment_text = language_manager.get_ui_text('overall_sentiment', current_lang)
                        
                        st.markdown(f"""
                            <div class='review-card'>
                                <h4 style='color: #ff4b4b; margin: 0;'>{review_number_text}{i}</h4>
                                <p style='margin: 0.5rem 0;'>{text}</p>
                            """, unsafe_allow_html=True)
                        
                        # Show original language if different from current UI language
                        if sentiment.get('original_language') and sentiment['original_language'] != 'en':
                            original_lang_name = language_manager.supported_languages.get(
                                sentiment['original_language'], {}
                            ).get('name', sentiment['original_language'])
                            original_language_text = language_manager.get_ui_text('original_language', current_lang)
                            st.markdown(f"<p><em>{original_language_text}: {original_lang_name}</em></p>", unsafe_allow_html=True)
                        
                        # Display sentiment in current language
                        sentiment_html = format_sentiment_multilingual(
                            sentiment['label'], 
                            sentiment['confidence'], 
                            current_lang
                        )
                        st.markdown(f"<p>{overall_sentiment_text}: {sentiment_html}</p>", unsafe_allow_html=True)
                        
                        # If aspect-specific question, show aspect sentiment
                        aspect = None
                        for key in ['food', 'service', 'ambience', 'price']:
                            if key in prompt_for_processing.lower():
                                aspect = key.capitalize()
                                aspect_sentiment = multilingual_analyzer.analyze_multilingual_aspect_sentiment(text, aspect)
                                if aspect_sentiment['aspect_mentioned']:
                                    aspect_sentiment_html = format_sentiment_multilingual(
                                        aspect_sentiment['label'], 
                                        aspect_sentiment['confidence'], 
                                        current_lang
                                    )
                                    st.markdown(
                                        f"<p>{aspect} Sentiment: {aspect_sentiment_html}</p>",
                                        unsafe_allow_html=True
                                    )
                        
                        # Add rating if available
                        if hasattr(review, 'metadata') and 'rating' in review.metadata:
                            rating = review.metadata['rating']
                            stars = '⭐' * int(rating)
                            rating_text = language_manager.get_ui_text('rating', current_lang)
                            st.markdown(f"<p>{rating_text}: {stars} ({rating}/5)</p>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)

                # Generate and display AI response
                analyzing_text = language_manager.get_ui_text('analyzing', current_lang)
                with st.spinner(analyzing_text):
                    reviews_with_sentiment = []
                    
                    # Format reviews with sentiment for AI processing
                    for review in reviews:
                        text = review.page_content
                        sentiment = multilingual_analyzer.analyze_multilingual_sentiment(text)
                        reviews_with_sentiment.append(f"{text} - {sentiment['label']}")
                    
                    # Get AI response
                    response = chain.invoke({
                        "reviews_with_sentiment": "\n".join(reviews_with_sentiment),
                        "sentiment_summary": "",
                        "question": prompt_for_processing
                    })
                    
                    # Translate response to user's preferred language if different from English
                    final_response = str(response)
                    if current_lang != 'en':
                        final_response = language_manager.translate_text(final_response, current_lang, 'en')
                    
                    # Add response to chat history
                    st.markdown(final_response)
                    st.session_state.messages.append({"role": "assistant", "content": final_response})
    
    # Chat controls
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        clear_chat_text = language_manager.get_ui_text('clear_chat', current_lang)
        if st.button(clear_chat_text, type="secondary"):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("📊 Show Stats", type="secondary"):
            if st.session_state.messages:
                user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
                assistant_messages = [msg for msg in st.session_state.messages if msg["role"] == "assistant"]
                
                st.info(f"""
                **Chat Statistics:**
                - Total messages: {len(st.session_state.messages)}
                - Your questions: {len(user_messages)}
                - AI responses: {len(assistant_messages)}
                """)
            else:
                st.info("No chat history yet. Start asking questions!")
    
    # Key features reminder
    with st.expander("🔧 Chat Features", expanded=False):
        real_time_sentiment = language_manager.get_ui_text('real_time_sentiment', current_lang)
        aspect_insights = language_manager.get_ui_text('aspect_insights', current_lang)
        review_summarization = language_manager.get_ui_text('review_summarization', current_lang)
        
        st.markdown(f"""
        ### Available Features:
        - **{real_time_sentiment}**: Automatic sentiment analysis of reviews
        - **{aspect_insights}**: Specific insights about food, service, ambience, and price
        - **{review_summarization}**: AI-powered summaries and recommendations
        - **Multilingual Support**: Ask questions in any supported language
        - **Context-Aware**: Responses based on relevant restaurant reviews
        
        ### Tips for Better Results:
        - Be specific in your questions (e.g., "food quality at Italian restaurants")
        - Ask about specific aspects (food, service, atmosphere, value)
        - Use natural language - the AI understands conversational queries
        """)
