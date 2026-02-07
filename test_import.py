try:
    import streamlit_agraph
    print(f"Success: {streamlit_agraph.__file__}")
except ImportError as e:
    print(f"Error: {e}")
