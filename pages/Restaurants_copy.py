import streamlit as st
import sys
import os
import json
import pandas as pd

# Add venv folder to Python path at the beginning to prioritize local modules
venv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'venv'))
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

# Try to import required modules with error handling
try:
    
    from multilingual_sentiment import multilingual_analyzer
    IMPORTS_AVAILABLE = True
    print("✅ Successfully imported sentiment analyzer in Restaurants.py")
    
except ImportError as e:
    print(f"❌ Import error in Restaurants.py: {str(e)}")
    IMPORTS_AVAILABLE = False
    # Create mock analyzer for testing
    class MockAnalyzer:
        def analyze_multilingual_sentiment(self, text):
            return {'label': 'neutral', 'confidence': 0.5, 'original_language': 'en'}
    
    multilingual_analyzer = MockAnalyzer()

def show_page(current_lang, language_manager):
    """Display the Restaurants page content"""
    
    st.markdown(f"""
        <div style='text-align: center; padding: 1rem;'>
            <h1 style='color: #ff4b4b; margin-bottom: 0;'>Restaurant Data</h1>
            <p style='font-style: italic; color: #666;'>Explore restaurant information and analytics</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Load restaurant data
    try:
        with open('data/restaurants.json', 'r') as f:
            restaurants_data = json.load(f)
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(restaurants_data)
        
        # Display summary statistics
        st.markdown("##  Restaurant Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label=" Total Restaurants",
                value=len(df),
                delta="Active listings"
            )
        
        with col2:
            avg_rating = df['rating'].mean() if 'rating' in df.columns else 0
            st.metric(
                label="⭐ Average Rating",
                value=f"{avg_rating:.1f}",
                delta="Out of 5.0"
            )
        
        with col3:
            cuisines = df['cuisine'].nunique() if 'cuisine' in df.columns else 0
            st.metric(
                label="🍴 Cuisine Types",
                value=cuisines,
                delta="Different varieties"
            )
        
        with col4:
            price_ranges = df['price_range'].nunique() if 'price_range' in df.columns else 0
            st.metric(
                label="💰 Price Ranges",
                value=price_ranges,
                delta="Budget options"
            )
        
        # Filters
        st.markdown("## 🔍 Filter Restaurants")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'cuisine' in df.columns:
                cuisine_options = ['All'] + sorted(df['cuisine'].unique().tolist())
                selected_cuisine = st.selectbox("Select Cuisine:", cuisine_options)
            else:
                selected_cuisine = 'All'
        
        with col2:
            if 'price_range' in df.columns:
                price_options = ['All'] + sorted(df['price_range'].unique().tolist())
                selected_price = st.selectbox("Select Price Range:", price_options)
            else:
                selected_price = 'All'
        
        with col3:
            if 'rating' in df.columns:
                min_rating = st.slider("Minimum Rating:", 0.0, 5.0, 0.0, 0.1)
            else:
                min_rating = 0.0
        
        # Apply filters
        filtered_df = df.copy()
        
        if selected_cuisine != 'All' and 'cuisine' in df.columns:
            filtered_df = filtered_df[filtered_df['cuisine'] == selected_cuisine]
        
        if selected_price != 'All' and 'price_range' in df.columns:
            filtered_df = filtered_df[filtered_df['price_range'] == selected_price]
        
        if 'rating' in df.columns:
            filtered_df = filtered_df[filtered_df['rating'] >= min_rating]
        
        # Display filtered results
        st.markdown(f"## 📋 Restaurant Listings ({len(filtered_df)} results)")
        
        if len(filtered_df) == 0:
            st.warning("No restaurants match your filter criteria. Please adjust your filters.")
        else:
            # Display restaurants in cards
            for idx, restaurant in filtered_df.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class='review-card' style='margin-bottom: 1rem;'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <h3 style='color: #ff4b4b; margin: 0;'>{restaurant.get('name', 'Unknown Restaurant')}</h3>
                                <div style='text-align: right;'>
                                    <span style='font-size: 1.2em;'>{'⭐' * int(restaurant.get('rating', 0))}</span>
                                    <span style='color: #666; margin-left: 0.5rem;'>({restaurant.get('rating', 'N/A')})</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Cuisine:** {restaurant.get('cuisine', 'Not specified')}")
                        st.write(f"**Address:** {restaurant.get('address', 'Not available')}")
                        if 'description' in restaurant:
                            st.write(f"**Description:** {restaurant['description']}")
                    
                    with col2:
                        st.write(f"**Price Range:** {restaurant.get('price_range', 'Not specified')}")
                        if 'phone' in restaurant:
                            st.write(f"**Phone:** {restaurant['phone']}")
                        if 'website' in restaurant:
                            st.write(f"**Website:** {restaurant['website']}")
                    
                    # Sample reviews analysis (if available)
                    if 'sample_reviews' in restaurant:
                        with st.expander(f"📝 Sample Reviews ({len(restaurant['sample_reviews'])} reviews)"):
                            for i, review in enumerate(restaurant['sample_reviews'][:3], 1):  # Show max 3 reviews
                                sentiment = multilingual_analyzer.analyze_multilingual_sentiment(review)
                                
                                sentiment_color = {
                                    'positive': '#28a745',
                                    'negative': '#dc3545',
                                    'neutral': '#6c757d'
                                }.get(sentiment['label'].lower(), '#6c757d')
                                
                                st.markdown(f"""
                                    <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin: 0.5rem 0;'>
                                        <p style='margin: 0; font-style: italic;'>"{review}"</p>
                                        <p style='margin: 0.5rem 0 0 0; color: {sentiment_color}; font-weight: bold;'>
                                            Sentiment: {sentiment['label'].title()} ({sentiment['confidence']:.2f})
                                        </p>
                                    </div>
                                """, unsafe_allow_html=True)
                    
                    st.markdown("---")
        
        # Analytics section
        if len(filtered_df) > 0:
            st.markdown("## 📈 Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'cuisine' in df.columns:
                    st.markdown("### 🍴 Cuisine Distribution")
                    cuisine_counts = filtered_df['cuisine'].value_counts()
                    st.bar_chart(cuisine_counts)
            
            with col2:
                if 'rating' in df.columns:
                    st.markdown("### ⭐ Rating Distribution")
                    rating_counts = filtered_df['rating'].value_counts().sort_index()
                    st.bar_chart(rating_counts)
            
            # Top rated restaurants
            if 'rating' in df.columns:
                st.markdown("### 🏆 Top Rated Restaurants")
                top_restaurants = filtered_df.nlargest(5, 'rating')[['name', 'cuisine', 'rating', 'price_range']]
                st.dataframe(top_restaurants, use_container_width=True)
    
    except FileNotFoundError:
        st.error("Restaurant data file not found. Please ensure 'data/restaurants.json' exists.")
        
        # Show sample data structure
        st.markdown("### 📋 Expected Data Structure")
        st.code("""
        [
            {
                "name": "Restaurant Name",
                "cuisine": "Italian",
                "rating": 4.5,
                "price_range": "$$",
                "address": "123 Main St",
                "phone": "+1-234-567-8900",
                "website": "https://example.com",
                "description": "Great Italian food...",
                "sample_reviews": [
                    "Amazing pasta and great service!",
                    "Good food but a bit expensive.",
                    "Love the atmosphere here."
                ]
            }
        ]
        """, language="json")
        
        # Create sample data button
        if st.button("🔧 Create Sample Data"):
            sample_data = [
                {
                    "name": "Bella Italia",
                    "cuisine": "Italian",
                    "rating": 4.5,
                    "price_range": "$$",
                    "address": "123 Main Street, Downtown",
                    "phone": "+1-234-567-8900",
                    "description": "Authentic Italian cuisine with fresh ingredients",
                    "sample_reviews": [
                        "Amazing pasta and great service!",
                        "The pizza was delicious but a bit expensive.",
                        "Love the cozy atmosphere here."
                    ]
                },
                {
                    "name": "Spice Garden",
                    "cuisine": "Indian",
                    "rating": 4.2,
                    "price_range": "$",
                    "address": "456 Oak Avenue, Midtown",
                    "phone": "+1-234-567-8901",
                    "description": "Traditional Indian dishes with authentic spices",
                    "sample_reviews": [
                        "Best curry in town!",
                        "Great value for money.",
                        "Service could be faster but food is excellent."
                    ]
                },
                {
                    "name": "Ocean Breeze",
                    "cuisine": "Seafood",
                    "rating": 4.8,
                    "price_range": "$$$",
                    "address": "789 Harbor Drive, Waterfront",
                    "phone": "+1-234-567-8902",
                    "description": "Fresh seafood with ocean views",
                    "sample_reviews": [
                        "Fresh lobster and amazing view!",
                        "Expensive but worth every penny.",
                        "Perfect for special occasions."
                    ]
                }
            ]
            
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Save sample data
            with open('data/restaurants.json', 'w') as f:
                json.dump(sample_data, f, indent=2)
            
            st.success("Sample restaurant data created! Please refresh the page.")
            st.rerun()
    
    except json.JSONDecodeError:
        st.error("Invalid JSON format in restaurant data file. Please check the file format.")
    
    except Exception as e:
        st.error(f"Error loading restaurant data: {str(e)}")
        st.info("Please check if the data file exists and is properly formatted.")
