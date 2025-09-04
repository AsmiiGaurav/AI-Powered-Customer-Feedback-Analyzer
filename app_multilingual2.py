import streamlit as st
import sys
import os
import mimetypes, base64, pathlib  # (safe to keep; not required for the bar)

# Add venv path to sys.path at the beginning to prioritize local modules
venv_path = os.path.join(os.path.dirname(__file__), 'venv')
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)  # Insert at beginning to prioritize over system modules

try:
    from main import chain
    from vector import retriever
    from multilingual_sentiment import multilingual_analyzer
    from language_config import language_manager
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all required modules are in the venv directory")
    st.stop()

# Set page configuration
st.set_page_config(
    page_title="Restaurant Review Analysis",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'en'
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'

# Hide Streamlit default menu and footer
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ===== Top bar backdrop (dark grey) + spacer ===============================
# ====== FIXED NAV BAR (buttons sit on the grey bar; no white gap) ======
# ===== Transparent fixed NAV over the hero (buttons on the image) =====
st.markdown("""
<style>
  /* Transparent bar that sits on top of the image */
  #rl-nav{
    position: fixed; top: 0; left: 0; right: 0;
    height: 72px;
    /* transparent, with a soft gradient for contrast over images */
    background: linear-gradient(to bottom, rgba(0,0,0,0.40), rgba(0,0,0,0.00));
    z-index: 999;
    pointer-events: none; /* allow widgets to still be clickable via inner container */
  }
  #rl-nav .rl-inner{
    max-width: 1200px;
    margin: 0 auto;
    padding: 12px 24px;
    pointer-events: auto; /* re-enable interactions on the inner nav */
  }

  /* IMPORTANT: no content offset — hero should start at the top */
  .block-container{ padding-top: 0 !important; }
  .stAppViewContainer, .main{ padding-top: 0 !important; }

  /* Remove stray top margin Streamlit sometimes adds around first block */
  .block-container > div:first-child{ margin-top: 0 !important; }

  /* Brand on transparent bar */
  .rl-brand{ color:#fff !important; text-shadow:0 1px 4px rgba(0,0,0,.5); }

  /* Buttons — same height as select */
  .stButton>button{
    background:#ff4b4b; color:#fff; border:none;
    height:40px; padding:0 16px; border-radius:20px;
    line-height:40px; display:inline-flex; align-items:center; justify-content:center;
    box-shadow:0 1px 3px rgba(0,0,0,.25);
  }
  .stButton>button:hover{ background:#ff2b2b; }

  /* Language select pill, readable on image */
  [data-testid="stSelectbox"] > div > div{
    background:rgba(34,34,34,.70) !important; border-radius:20px !important;
    border:1px solid rgba(255,255,255,.25) !important;
    height:40px; padding:0 14px !important;
    display:inline-flex !important; align-items:center !important;
    min-width:180px; white-space:nowrap;
    box-shadow:0 1px 3px rgba(0,0,0,.25);
  }
  [data-testid="stSelectbox"] > div > div:hover{ background:rgba(34,34,34,.85) !important; }
  [data-testid="stSelectbox"] > div > div > div{
    color:#fff !important; font-weight:600 !important; overflow:visible !important;
  }
  [data-testid="stSelectbox"] svg{ fill:#fff !important; }
</style>

<div id="rl-nav"><div class="rl-inner">
""", unsafe_allow_html=True)

# NAV ROW lives inside the fixed transparent bar
col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

with col1:
    st.markdown("""
        <div style='display: flex; align-items: center;'>
            <h3 style='margin: 0; color: #ff4b4b; font-size: 1.5rem; font-weight: 800;'>
                RestaurantLens
            </h3>
        </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button(" Home", key="home_btn", type="primary" if st.session_state.current_page == "Home" else "secondary"):
        st.session_state.current_page = "Home"; st.rerun()

with col3:
    if st.button(" Explore", key="explore_btn", type="primary" if st.session_state.current_page == "Restaurants" else "secondary"):
        st.session_state.current_page = "Restaurants"; st.rerun()

with col4:
    if st.button(" Chat", key="chat_btn", type="primary" if st.session_state.current_page == "Chat" else "secondary"):
        st.session_state.current_page = "Chat"; st.rerun()

with col5:
    language_options = language_manager.get_language_options()
    selected_lang_display = st.selectbox(
        "Language",
        options=list(language_options.keys()),
        format_func=lambda x: language_options[x],
        index=list(language_options.keys()).index(st.session_state.selected_language),
        key="language_selector",
        label_visibility="collapsed"
    )
    if selected_lang_display != st.session_state.selected_language:
        st.session_state.selected_language = selected_lang_display
        st.rerun()

st.markdown("</div></div>", unsafe_allow_html=True)


# Get current language
current_lang = st.session_state.selected_language

# Custom CSS with RTL support
rtl_style = ""
if language_manager.is_rtl_language(current_lang):
    rtl_style = """
        .main { direction: rtl; }
        .stChatMessage { direction: rtl; text-align: right; }
        [data-testid="stChatMessageContent"] { direction: rtl; text-align: right; }
    """

st.markdown(f"""
    <style>
        /* App background */
        .main {{
            background-image: url('https://images.unsplash.com/photo-1495195134817-aeb325a55b65?ixlib=rb-4.0.3');
            background-size: cover;
        }}
        .stApp {{
            background: rgba(255, 255, 255, 0.92);
        }}

        /* Reduce Streamlit's default extra padding at the very top of the main block */
        .main > div:first-child {{
            padding-top: 0 !important;
        }}

        /* Chat + sidebar look */
        .stChatMessage {{ color: #1a1a1a !important; }}
        [data-testid="stChatMessageContent"] {{
            background-color: #f0f2f6 !important;
            color: #1a1a1a !important;
        }}
        [data-testid="stSidebar"] {{
            background-color: rgba(0, 0, 0, 0.8) !important;
            color: white !important;
        }}
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] ul,
        [data-testid="stSidebar"] li {{ color: white !important; }}

        .element-container .stMarkdown {{ color: #1a1a1a !important; }}
        .stChatInputContainer {{ background-color: white !important; }}

        /* --- Nav buttons: uniform size so they align with the selectbox --- */
        .stButton>button {{
            background-color: #ff4b4b;
            color: white;
            border: none;
            height: 40px;                /* fixed height to match select */
            padding: 0 16px;
            border-radius: 20px;
            line-height: 40px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}
        .stButton>button:hover {{ background-color: #ff2b2b; }}

        /* --- Language select styled as a pill and aligned with buttons --- */
        [data-testid="stSelectbox"] > div > div {{
            background-color: #ff4b4b !important;
            border-radius: 20px !important;
            border: none !important;
            height: 40px;                /* same as buttons */
            padding: 0 16px !important;
            display: inline-flex !important;
            align-items: center !important;
            min-width: 170px;            /* ensure text is visible */
            white-space: nowrap;
        }}
        [data-testid="stSelectbox"] > div > div:hover {{
            background-color: #ff2b2b !important;
        }}
        [data-testid="stSelectbox"] > div > div > div {{
            color: white !important;
            font-weight: 600 !important;
            overflow: visible !important;
        }}
        /* dropdown arrow color */
        [data-testid="stSelectbox"] svg {{ fill: white !important; }}

        /* remove hacky negative margins; align naturally */
        .stSelectbox {{ margin-top: 0 !important; }}

        /* Cards/expanders etc. */
        div[data-testid="stExpander"] {{
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            border: 1px solid #ff4b4b;
            padding: 10px;
        }}

        .sentiment-positive {{ color: #28a745; font-weight: bold; }}
        .sentiment-negative {{ color: #dc3545; font-weight: bold; }}
        .sentiment-neutral  {{ color: #6c757d; font-weight: bold; }}

        .review-card {{
            background-color: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }}
        .language-badge {{
            background-color: #007bff;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-left: 5px;
        }}

        {rtl_style}
    </style>
    """, unsafe_allow_html=True)

# Sidebar
# with st.sidebar:
#     st.markdown("<hr style='border-color: rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
#     st.markdown("###  Navigation")
#     pages = {
#         "Home": " Home",
#         "Chat": " Chat Analysis",
#         "Restaurants": " Restaurant Data"
#     }
#     selected_page = st.session_state.current_page
#     st.info(f"Current Page: {pages.get(selected_page, selected_page)}")

# Import and display the selected page based on session state
if st.session_state.current_page == "Home":
    try:
        from pages import Home
        Home.show_page(current_lang, language_manager)
    except ImportError:
        st.error("Home page not found. Please check the pages/Home.py file.")
elif st.session_state.current_page == "Chat":
    try:
        from pages import Chat
        Chat.show_page(current_lang, language_manager)
    except ImportError:
        st.error("Chat page not found. Please check the pages/Chat.py file.")
elif st.session_state.current_page == "Restaurants":
    try:
        from pages import Restaurants
        Restaurants.show_page(current_lang, language_manager)
    except ImportError:
        st.error("Restaurants page not found. Please check the pages/Restaurants.py file.")

# with st.sidebar:
#     st.markdown("<hr style='border-color: rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
#     st.markdown("### ℹ About")
#     st.markdown("Multi-page Restaurant Review Analysis App with multilingual support")
 
