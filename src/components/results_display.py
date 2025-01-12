import streamlit as st
from datetime import datetime
from urllib.parse import urlparse
from ..utils.screenshot import create_thumbnail, create_zip_file

def clear_results():
    """Limpia los resultados y reinicia el estado"""
    st.session_state.screenshots_data = {}
    st.session_state.show_results = False
    st.rerun()

def get_device_name(resolution_name):
    """Get device name from resolution name"""
    if "Desktop" in resolution_name:
        return "💻 Desktop"
    elif "Tablet" in resolution_name:
        return "📱 Tablet"
    elif "Mobile" in resolution_name:
        return "📱 Mobile"
    else:
        return "📱 Custom"

def display_screenshot(url, screenshot_data, resolution_name):
    """Display a single screenshot with its resolution name"""
    device = get_device_name(resolution_name)
    domain = urlparse(url).netloc
    
    with st.expander(f"{domain} - {device}", expanded=False):
        st.image(screenshot_data, use_column_width=True)

def results_section():
    """Component for displaying screenshot results"""
    if "screenshots_data" in st.session_state and st.session_state.screenshots_data:
        st.markdown("<div class='results-container'>", unsafe_allow_html=True)
        
        # Header con botones de acción
        col1, col2 = st.columns([1, 4])
        with col1:
            # Botón de descarga ZIP
            st.download_button(
                "📦 Download ZIP",
                data=create_zip_file(st.session_state.screenshots_data),
                file_name=f"screenshots_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True
            )
        with col2:
            # Botón para limpiar resultados
            if st.button("Clear Results", type="secondary", key="clear_results", use_container_width=True):
                st.session_state.screenshots_data = {}
                st.rerun()
        
        # Display screenshots
        for url, resolutions in st.session_state.screenshots_data.items():
            for resolution_name, screenshot_data in resolutions.items():
                display_screenshot(url, screenshot_data, resolution_name)
        
        st.markdown("</div>", unsafe_allow_html=True) 