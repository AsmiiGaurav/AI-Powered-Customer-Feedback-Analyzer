import streamlit as st
import sys
import os
import json
import pandas as pd

# Add venv folder to Python path at the beginning to prioritize local modules
venv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'venv'))
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

def show_page(current_lang, language_manager):
    """Display the Restaurants page content"""

    st.markdown(f"""
        <div style='text-align: center; padding: 1rem;'>
            <h1 style='color: #ff4b4b; margin-bottom: 0;'>Top Restaurants</h1>
            <p style='font-style: italic; color: #666;'>Browse, search, and explore restaurant listings</p>
        </div>
        """, unsafe_allow_html=True)

    # Load restaurant data
    try:
        with open('data/restaurants.json', 'r') as f:
            restaurants_data = json.load(f)

        # Convert to DataFrame
        df = pd.DataFrame(restaurants_data)

        # --- Search Bar ---
        search_query = st.text_input("🔍 Search Restaurants", placeholder="Type a restaurant name...").strip().lower()

        # --- Filters ---
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

        # --- Apply filters ---
        filtered_df = df.copy()

        if search_query:
            filtered_df = filtered_df[filtered_df['name'].str.lower().str.contains(search_query)]

        if selected_cuisine != 'All':
            filtered_df = filtered_df[filtered_df['cuisine'] == selected_cuisine]

        if selected_price != 'All':
            filtered_df = filtered_df[filtered_df['price_range'] == selected_price]

        filtered_df = filtered_df[filtered_df['rating'] >= min_rating]

        # --- Restaurant Listings ---
        st.markdown(f"## 📋 Restaurant Listings ({len(filtered_df)} results)")

        if len(filtered_df) == 0:
            st.warning("No restaurants match your search or filter criteria. Try adjusting them.")
        else:
            cols = st.columns(2)  # 2-column grid
            for idx, restaurant in filtered_df.iterrows():
                col = cols[idx % 2]  # alternate between 2 columns
                with col:
                    with st.container():
                        # Card style
                        st.markdown(
                            """
                            <style>
                                .restaurant-card {
                                    background: white;
                                    padding: 1rem;
                                    margin-bottom: 1.5rem;
                                    border-radius: 12px;
                                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                                }
                                .restaurant-title {
                                    color: #ff4b4b;
                                    margin: 0;
                                    font-size: 1.3rem;
                                    font-weight: bold;
                                }
                                .restaurant-rating {
                                    color: #ffa500;
                                    font-size: 1.1rem;
                                    font-weight: 600;
                                }
                            </style>
                            """,
                            unsafe_allow_html=True
                        )

                        st.markdown("<div class='restaurant-card'>", unsafe_allow_html=True)

                        # Layout: image + details
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            img_path = restaurant.get("image", None)
                            if img_path and os.path.exists(img_path):
                                st.image(img_path, use_container_width=True)
                            else:
                                st.image("assets/restaurants/placeholder.jpg", use_container_width=True)

                        with c2:
                            st.markdown(f"<p class='restaurant-title'>{restaurant.get('name','Unknown')}</p>",
                                        unsafe_allow_html=True)
                            st.write(f"**Cuisine:** {restaurant.get('cuisine','N/A')}")
                            st.write(f"**Address:** {restaurant.get('address','N/A')}")
                            st.write(f"**Rating:** ⭐ {restaurant.get('rating','N/A')}")
                            st.write(f"**Price Range:** {restaurant.get('price_range','N/A')}")
                            st.write(restaurant.get("description","No description available."))

                        # Reviews Expander
                        if 'sample_reviews' in restaurant and len(restaurant['sample_reviews']) > 0:
                            with st.expander(f"📝 Reviews ({len(restaurant['sample_reviews'])})"):
                                for review in restaurant['sample_reviews']:
                                    st.markdown(
                                        f"""
                                        <div style='background:#f8f9fa; padding:0.8rem; border-radius:8px; margin:0.5rem 0;'>
                                            <p style='margin:0; font-style: italic;'>"{review}"</p>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )

                        st.markdown("</div>", unsafe_allow_html=True)

    except FileNotFoundError:
        st.error("❌ Restaurant data file not found. Please ensure 'data/restaurants.json' exists.")
    except Exception as e:
        st.error(f"⚠️ Error loading restaurant data: {str(e)}")
