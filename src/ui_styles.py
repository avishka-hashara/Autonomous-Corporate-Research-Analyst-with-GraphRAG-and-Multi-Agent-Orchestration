import streamlit as st

def apply_custom_css():
    """Applies custom CSS to the Streamlit app for a modern, 'cool' look."""
    st.markdown("""
        <style>
            /* Import Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

            /* Global Styles */
            html, body, [class*="css"] {
                font-family: 'Outfit', sans-serif;
            }
            
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Outfit', sans-serif;
                font-weight: 700;
                letter-spacing: -0.5px;
            }
            
            code {
                font-family: 'JetBrains Mono', monospace;
            }

            /* Main Container Background */
            .stApp {
                background-color: #050505;
                background-image: 
                    radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
                    radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
                    radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
                color: #FAFAFA;
            }

            /* Sidebar Styling */
            section[data-testid="stSidebar"] {
                background-color: rgba(10, 10, 15, 0.8);
                backdrop-filter: blur(12px);
                border-right: 1px solid rgba(255, 255, 255, 0.05);
            }

            /* Header Styling - Gradient Text */
            h1 {
                background: linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 30px rgba(0, 201, 255, 0.3);
            }
            
            h2, h3 {
                color: #E0E0E0;
            }

            /* Buttons - Neon Glow */
            .stButton > button {
                background: linear-gradient(90deg, #0061ff 0%, #60efff 100%);
                color: #000;
                font-weight: 600;
                border: none;
                border-radius: 8px;
                padding: 0.6rem 1.2rem;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(0, 97, 255, 0.4);
                color: #000;
            }
            
            /* Secondary Buttons (Delete etc) */
            div[data-testid="stVerticalBlock"] > div > div > div > div > button {
               /* This is a bit hacky for specific buttons but general secondary style */
               border: 1px solid rgba(255,255,255,0.1);
            }

            /* Chat Messages */
            .stChatMessage {
                background-color: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 1rem;
                margin-bottom: 1rem;
            }
            
            /* Card-like Containers */
            div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
                background-color: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 1.5rem;
            }

            /* Input Fields */
            .stTextInput > div > div > input {
                background-color: rgba(0, 0, 0, 0.3);
                color: #FFF;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
            .stTextInput > div > div > input:focus {
                border-color: #00C9FF;
                box-shadow: 0 0 10px rgba(0, 201, 255, 0.2);
            }

            /* Tabs */
            .stTabs [data-baseline-toggle="true"] {
                background-color: transparent;
            }
            .stTabs [aria-selected="true"] {
                color: #00C9FF !important;
                border-bottom-color: #00C9FF !important;
            }
            
            /* Status/Expander */
            .streamlit-expanderHeader {
                background-color: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.05);
                color: #FFF;
            }
            
            /* Toast */
            div[data-testid="stToast"] {
                background-color: #1A1A1A;
                border: 1px solid #333;
                color: #FFF;
            }

        </style>
    """, unsafe_allow_html=True)

def render_header():
    """Renders a custom header with a modern subheader."""
    st.markdown("""
        <div style="text-align: center; margin-bottom: 3rem; margin-top: 1rem;">
            <div style="display: inline-block; padding: 0.5rem 1rem; border-radius: 20px; background: rgba(0, 201, 255, 0.1); color: #00C9FF; font-size: 0.8rem; margin-bottom: 0.5rem; border: 1px solid rgba(0, 201, 255, 0.2);">
                POWERED BY TIDB & LLAMA 3
            </div>
            <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem;">Corporate Analyst Agent</h1>
            <p style="color: #8B949E; font-size: 1.2rem; max-width: 600px; margin: 0 auto;">
                Autonomous research assistant capable of 
                knowledge graph extraction and vector-based strategy analysis.
            </p>
        </div>
    """, unsafe_allow_html=True)
