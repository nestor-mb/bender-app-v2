import streamlit as st
from datetime import datetime
from urllib.parse import urlparse
from ..utils.screenshot import create_thumbnail, create_zip_file
from ..config.constants import RESOLUTIONS

def clear_results():
    """Limpia los resultados y reinicia el estado"""
    st.session_state.screenshots_data = {}
    st.session_state.show_results = False
    st.rerun()

def results_section():
    """Component for displaying screenshot results"""
    if not st.session_state.show_results or not st.session_state.screenshots_data:
        return

    with st.container():
        st.markdown("<div class='section-container results-container'>", unsafe_allow_html=True)
        
        # Header con botón de limpiar
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Results")
        with col2:
            if st.button("🧹 Clear Results", type="secondary", use_container_width=True):
                clear_results()
                return
        
        # Download options
        col1, col2 = st.columns([1, 4])
        with col1:
            st.download_button(
                "📦 Download All (ZIP)",
                data=create_zip_file(st.session_state.screenshots_data),
                file_name=f"screenshots_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True
            )
        
        # Results display
        for url in st.session_state.screenshots_data:
            screenshots = st.session_state.screenshots_data[url]
            
            for resolution_name, screenshot in screenshots.items():
                expander_title = f"📸 {url} - {resolution_name}"
                
                with st.expander(expander_title, expanded=False):
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.download_button(
                            "📥 Download",
                            data=screenshot,
                            file_name=f"{urlparse(url).netloc}_{resolution_name.split()[0].lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                            mime="image/png",
                            key=f"download_{url}_{resolution_name}",
                            use_container_width=True
                        )
                    
                    with col2:
                        st.image(
                            screenshot,
                            use_container_width=True,
                            output_format="PNG"
                        )
        
        st.markdown("</div>", unsafe_allow_html=True) 