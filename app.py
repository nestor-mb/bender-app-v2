import streamlit as st
import os

# Import components
from src.components.url_input import url_input_section
from src.components.queue_manager import queue_manager_section
from src.components.results_display import results_section
from src.config.constants import PAGE_CONFIG

# Load CSS
def load_css():
    with open(os.path.join("src", "styles", "main.css")) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize app
def init_app():
    # Set page config
    st.set_page_config(**PAGE_CONFIG)
    
    # Initialize session state
    if 'urls_queue' not in st.session_state:
        st.session_state.urls_queue = []
    if 'screenshots_data' not in st.session_state:
        st.session_state.screenshots_data = {}
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False

def main():
    try:
        # Initialize app
        init_app()
        
        # Load CSS
        load_css()
        
        # URL Input Section
        url_input_section()
        
        # Queue Manager Section
        queue_manager_section()
        
        # Results Section
        results_section()
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()