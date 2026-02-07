import streamlit as st

def apply_custom_css():
    """Applies custom CSS to the Streamlit app for a modern, 'cool' look."""
    st.markdown("""
        <style>
            /* Import Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

            /* Global Styles */
            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }

            /* Main Container Background */
            .stApp {
                background-color: #0E1117; /* Dark background */
                color: #FAFAFA;
            }

            /* Sidebar Styling */
            [data-testid="stSidebar"] {
                background-color: #161B22; /* Slightly lighter dark for sidebar */
                border-right: 1px solid #30363D;
            }

            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
                color: #58A6FF; /* Accent blue */
            }

            /* Header Styling */
            h1, h2, h3 {
                color: #FFFFFF;
                font-weight: 700;
            }
            
            h1 {
                background: -webkit-linear-gradient(45deg, #58A6FF, #BC8CFF);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            /* Button Styling */
            .stButton > button {
                background-color: #238636;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0.5rem 1rem;
                transition: all 0.2s ease;
            }
            .stButton > button:hover {
                background-color: #2EA043;
                box-shadow: 0 4px 12px rgba(46, 160, 67, 0.4);
                transform: translateY(-1px);
            }

            /* Chat Message Bubbles (Standard Streamlit chat messages are hard to customize deeply, 
               but we can tweak the container if possible or just rely on st.chat_message execution) */
            
            /* Customize the chat avatars if we were using custom HTML, 
               but Streamlit's native chat is encapsulated. */

            /* Expander / Status styling */
            .streamlit-expanderHeader {
                background-color: #21262D;
                border-radius: 6px;
                border: 1px solid #30363D;
            }
            
            /* Input fields */
            .stTextInput > div > div > input {
                background-color: #0D1117;
                color: #C9D1D9;
                border: 1px solid #30363D;
                border-radius: 6px;
            }
            .stTextInput > div > div > input:focus {
                border-color: #58A6FF;
                box-shadow: 0 0 0 1px #58A6FF;
            }

            /* Spinner custom color (limited support via CSS but we try) */
            .stSpinner > div {
                border-top-color: #58A6FF !important;
            }
            
            /* Tabs */
            .stTabs [data-baseline-toggle="true"] {
                background-color: transparent;
            }
            .stTabs [aria-selected="true"] {
                color: #58A6FF !important;
                border-bottom-color: #58A6FF !important;
            }

        </style>
    """, unsafe_allow_html=True)

def render_header():
    """Renders a custom header."""
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1>🤖 Corporate Analyst Agent</h1>
            <p style="color: #8B949E; font-size: 1.1rem;">
                Advanced AI Analysis & Knowledge Graph Exploration
            </p>
        </div>
    """, unsafe_allow_html=True)
