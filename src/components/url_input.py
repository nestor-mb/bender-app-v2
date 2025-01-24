import streamlit as st
from ..utils.validation import validate_url

def show_help_modal():
    st.markdown("""
        <div class="help-text">
            <p><strong>Instrucciones:</strong></p>
            <ul>
                <li>Ingresa una URL para capturar una sola página</li>
                <li>Ingresa múltiples URLs separadas por comas o nuevas líneas</li>
                <li>Sube un archivo CSV con una columna de URLs</li>
                <li>Selecciona la resolución deseada para las capturas</li>
                <li>Haz clic en "Capturar" para procesar las URLs</li>
            </ul>
            <p><em>Nota: Las URLs deben comenzar con http:// o https://</em></p>
        </div>
    """, unsafe_allow_html=True)

def url_input_section():
    """Component for URL input section"""
    with st.container():
        st.markdown("<div class='section-container'>", unsafe_allow_html=True)
        
        # URL Input
        url_input = st.text_area(
            "Enter URL(s)",
            placeholder="https://example.com\nhttps://another-example.com",
            help="Enter one or multiple URLs, each on a new line"
        )
        
        # Drag and drop file uploader
        uploaded_file = st.file_uploader(
            "Or upload a CSV file with URLs",
            type=["csv", "txt"],
            help="Upload a file containing one URL per line",
            label_visibility="collapsed"
        )
        
        # Add a question mark icon for help with expander
        with st.expander("Help", expanded=False):
            st.markdown("""
                To upload a CSV file, please follow these guidelines:
                - The file should contain one URL per line.
                - Ensure that the file is in CSV format.
                - The maximum file size is 200MB.
                - Example of a valid CSV file:
                  ```
                  https://example.com
                  https://another-example.com
                  ```
            """)
        
        if st.button("Add to Queue", type="primary"):
            new_urls = []
            if url_input:
                new_urls.extend([url.strip() for url in url_input.split('\n') if url.strip()])
            if uploaded_file:
                new_urls.extend(uploaded_file.read().decode("utf-8").splitlines())
            
            valid_urls = [url for url in new_urls if validate_url(url)]
            st.session_state.urls_queue.extend(valid_urls)
            
            if valid_urls:
                st.success(f"✅ Added {len(valid_urls)} URLs to the queue")
                if len(new_urls) > len(valid_urls):
                    st.warning(f"⚠️ {len(new_urls) - len(valid_urls)} invalid URLs were skipped")
        
        st.markdown("</div>", unsafe_allow_html=True) 