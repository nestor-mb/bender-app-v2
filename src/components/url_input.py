import streamlit as st
from ..utils.validation import validate_url

def url_input_section():
    """Component for URL input section"""
    with st.container():
        st.markdown("<div class='section-container'>", unsafe_allow_html=True)
        
        # URL Input
        url_input = st.text_area(
            "Enter URL(s)",
            placeholder="Enter one or multiple URLs (one per line)\nExample:\nhttps://example.com\nhttps://another-example.com",
            help="Enter one or multiple URLs, each on a new line"
        )
        
        col1, col2 = st.columns([4, 1])
        with col1:
            # File uploader for CSV
            uploaded_file = st.file_uploader(
                "Or upload a CSV file with URLs",
                type=["csv", "txt"],
                help="Upload a file containing one URL per line",
                label_visibility="collapsed"
            )
        
        with col2:
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