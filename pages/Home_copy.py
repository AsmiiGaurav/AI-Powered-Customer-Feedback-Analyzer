import base64, mimetypes, pathlib
import streamlit as st

def get_data_url(path: str) -> str:
    p = pathlib.Path(path)
    if not p.exists():
        st.error(f"Image not found: {p.resolve()}")
        return ""
    mime, _ = mimetypes.guess_type(str(p))
    if mime is None:
        mime = "image/png"  # safe default
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"

bg_img_url = get_data_url("assets/images/foodbg.png")  # your rotated image

def show_page(current_lang, language_manager):
    # ---------- HERO SECTION ----------
    st.markdown(
        f"""
        <style>
            .hero-section {{
                position: relative;
                height: 50vh;                      /* Top half of screen */
                width: 100vw;                      /* Full width */
                margin-left: calc(50% - 50vw);     /* Escape Streamlit layout */
                margin-top: 1rem;                  /* Add space from nav bar */
                background-image: url('{bg_img_url}');
                background-size: cover;
                background-position: center;
                display: flex;
                justify-content: center;
                align-items: center;
                text-align: center;
                color: white;
            }}
            .hero-overlay {{
                position: absolute; 
                inset: 0;
                background: rgba(0,0,0,0.4);       /* Dark overlay for text readability */
            }}
            .hero-content {{
                position: relative;
                z-index: 2;
                padding: 2rem;
            }}
            .hero-content h1 {{
                font-size: clamp(2.5rem, 6vw, 4rem);
                font-weight: 800;
                margin: 0 0 1rem 0;
                text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
                color: white;
                letter-spacing: -1px;
            }}
            .hero-content p {{
                font-size: clamp(1.2rem, 3vw, 1.8rem);
                font-weight: 300;
                margin: 0;
                text-shadow: 1px 1px 4px rgba(0,0,0,0.8);
                color: white;
                opacity: 0.95;
            }}
        </style>

        <div class="hero-section">
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <h1>🍽️ RestaurantLens</h1>
                <p>AI-Powered Restaurant Review Analysis Tool</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Add some spacing after hero section
    st.markdown('<div style="padding-top: 3rem;"></div>', unsafe_allow_html=True)


    
    # Welcome section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div style='background-color: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 2rem 0;'>
                <h2 style='text-align: center; color: #ff4b4b; margin-bottom: 1.5rem;'>Welcome to Our Platform</h2>
                <p style='text-align: center; font-size: 1.1rem; line-height: 1.6; color: #333;'>
                    Discover insights from restaurant reviews using advanced AI and multilingual sentiment analysis. 
                    Navigate through our interactive pages to explore restaurant data and chat with our AI assistant.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Features section with modern cards
    st.markdown("""
        <div style='padding: 4rem 2rem; text-align: center;'>
            <h2 style='color: #333; margin-bottom: 3rem; font-weight: 600;'>Why Choose Our Platform?</h2>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style='background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 250px; transition: transform 0.3s ease;' onmouseover='this.style.transform="translateY(-5px)"' onmouseout='this.style.transform="translateY(0)"'>
                <div style='text-align: center;'>
                    <h3 style='color: #ff4b4b; margin-bottom: 1rem; font-size: 1.8rem;'>AI-Powered Chat</h3>
                    <p style='color: #666; line-height: 1.6; font-size: 1.1rem;'>
                        Get instant insights from our intelligent chatbot. Ask questions about restaurants and receive detailed analysis of customer reviews.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style='background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 250px; transition: transform 0.3s ease;' onmouseover='this.style.transform="translateY(-5px)"' onmouseout='this.style.transform="translateY(0)"'>
                <div style='text-align: center;'>
                    <h3 style='color: #ff4b4b; margin-bottom: 1rem; font-size: 1.8rem;'>Global Reach</h3>
                    <p style='color: #666; line-height: 1.6; font-size: 1.1rem;'>
                        Break language barriers with our multilingual support. Analyze reviews in multiple languages with accurate sentiment analysis.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style='background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 250px; transition: transform 0.3s ease;' onmouseover='this.style.transform="translateY(-5px)"' onmouseout='this.style.transform="translateY(0)"'>
                <div style='text-align: center;'>
                    <h3 style='color: #ff4b4b; margin-bottom: 1rem; font-size: 1.8rem;'>Deep Insights</h3>
                    <p style='color: #666; line-height: 1.6; font-size: 1.1rem;'>
                        Uncover trends and patterns with advanced analytics. Get comprehensive sentiment analysis and detailed reports.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Quick start guide
    st.markdown("## Quick Start Guide")

    with st.expander("How to use this application", expanded=True):
        st.markdown("""
        ### Step 1: Choose Your Language
        - Use the language selector in the top bar to choose your preferred language
        - The interface will automatically translate to your selected language

        ### Step 2: Navigate Between Pages
        - **Home**: Overview and welcome page (you are here!)
        - **Chat Analysis**: Interactive AI chat for restaurant queries
        - **Restaurant Data**: Browse and analyze restaurant information

        ### Step 3: Start Exploring
        - Go to the Chat page to ask questions about restaurants
        - Visit the Restaurant Data page to see detailed analytics
        - All features support multilingual input and output
        
        ### Example Questions You Can Ask:
        - "What do customers say about the food quality?"
        - "Which restaurants have the best service?"
        - "Show me reviews about Italian restaurants"
        - "What are the common complaints about restaurants?"
        """)
    
    # Stats section with modern design
    st.markdown("""
        <div style='padding: 6rem 2rem 4rem; text-align: center; background: rgba(255, 255, 255, 0.9); margin: 4rem auto; border-radius: 20px; max-width: 1000px;'>
            <h2 style='color: #333; margin-bottom: 3rem; font-weight: 600;'>Our Impact in Numbers</h2>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div style='text-align: center;'>
                <h3 style='color: #ff4b4b; font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;'>500+</h3>
                <p style='color: #666; font-size: 1.1rem;'>Restaurants Analyzed</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style='text-align: center;'>
                <h3 style='color: #ff4b4b; font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;'>10K+</h3>
                <p style='color: #666; font-size: 1.1rem;'>Reviews Processed</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style='text-align: center;'>
                <h3 style='color: #ff4b4b; font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;'>15+</h3>
                <p style='color: #666; font-size: 1.1rem;'>Languages Supported</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div style='text-align: center;'>
                <h3 style='color: #ff4b4b; font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;'>95%</h3>
                <p style='color: #666; font-size: 1.1rem;'>Analysis Accuracy</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Final CTA section
    st.markdown("""
        <div style='text-align: center; padding: 6rem 2rem; margin-top: 4rem;'>
            <h2 style='color: #333; font-weight: 600; margin-bottom: 1.5rem;'>Ready to Get Started?</h2>
            <p style='color: #666; font-size: 1.2rem; margin-bottom: 2rem;'>Begin analyzing restaurant reviews and unlock valuable insights today.</p>
            <button class='cta-button' onclick='window.location.href="#explore"' style='font-size: 1.2rem;'>
                Explore Reviews Now →
            </button>
        </div>
        """, unsafe_allow_html=True)
