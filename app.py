import streamlit as st
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import validators
from datetime import datetime
import pandas as pd
import zipfile
from urllib.parse import urlparse

# Page Configuration
st.set_page_config(
    page_title="Screenshot Generator Pro",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    /* Main container */
    .main {
        padding: 2rem;
    }
    
    /* Headers */
    h1 {
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* User info box */
    .user-info {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 2rem;
        text-align: center;
        color: #6c757d;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 0.5rem;
    }
    
    /* Select boxes */
    .stSelectbox > div > div > div {
        border-radius: 0.5rem;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 0.5rem;
        background-color: #1E88E5;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 500;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #1976D2;
        border: none;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5;
        color: white;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #1E88E5;
    }
    
    /* Error messages */
    .stAlert {
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

def validate_url(url):
    """Validate URL with user feedback"""
    if not url:
        st.warning("⚠️ Please enter a URL")
        return False
    if not url.startswith(('http://', 'https://')):
        st.warning("⚠️ URL must start with http:// or https://")
        return False
    if not validators.url(url):
        st.error("❌ Invalid URL format")
        return False
    return True

def setup_webdriver():
    """Configure and return Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        st.error(f"❌ Error configuring WebDriver: {str(e)}")
        return None

def capture_screenshot(url, width, height, options):
    """Capture screenshot with retry logic"""
    start_time = time.time()
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            driver = setup_webdriver()
            if not driver:
                return None, time.time() - start_time

            driver.set_window_size(width, height)
            driver.get(url)

            # Wait for page load
            time.sleep(options.get('wait_time', 3))

            # Handle cookie banners
            if options.get('hide_cookie_banners', True):
                try:
                    cookie_buttons = WebDriverWait(driver, 5).until(
                        EC.presence_of_all_elements_located((By.XPATH, 
                            "//button[contains(text(), 'Accept') or contains(text(), 'Agree')]"
                        ))
                    )
                    for button in cookie_buttons:
                        driver.execute_script("arguments[0].click();", button)
                except:
                    pass

            # Take screenshot
            screenshot = driver.get_screenshot_as_png()
            driver.quit()
            return screenshot, time.time() - start_time

        except Exception as e:
            if driver:
                driver.quit()
            if attempt == max_retries - 1:
                st.error(f"❌ Failed after {max_retries} attempts: {str(e)}")
                return None, time.time() - start_time
            time.sleep(2 ** attempt)

    return None, time.time() - start_time

def get_advanced_options():
    """Display and collect advanced screenshot options"""
    with st.expander("🛠️ Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            wait_time = st.slider(
                "Page Load Wait Time (seconds)", 
                min_value=1, 
                max_value=10, 
                value=3
            )
            
            hide_cookie_banners = st.checkbox(
                "Auto-hide Cookie Banners", 
                value=True
            )

        with col2:
            full_page = st.checkbox(
                "Capture Full Page", 
                value=True
            )

        return {
            "wait_time": wait_time,
            "full_page": full_page,
            "hide_cookie_banners": hide_cookie_banners
        }

def main():
    st.title("🖼️ Website Screenshot Generator Pro")
    st.markdown("""
        Generate high-quality screenshots of any website with advanced customization options.
        Perfect for documentation, testing, and archival purposes.
    """)
    
    # Main content tabs
    tab1, tab2 = st.tabs(["📸 Single URL", "📑 Batch Processing"])

    with tab1:
        website_url = st.text_input(
            "Enter website URL",
            placeholder="https://example.com"
        )

        # Resolution selection
        col1, col2 = st.columns([2, 1])
        with col1:
            resolution_options = {
                "Desktop (1920x1080)": (1920, 1080),
                "Tablet (768x1024)": (768, 1024),
                "Mobile (375x812)": (375, 812),
                "Custom": "custom"
            }
            
            selected_resolution = st.selectbox(
                "Select Device Resolution",
                options=list(resolution_options.keys())
            )
        
        # Handle custom resolution
        if selected_resolution == "Custom":
            col1, col2 = st.columns(2)
            with col1:
                width = st.number_input("Width (px)", value=1024, min_value=200, max_value=3840)
            with col2:
                height = st.number_input("Height (px)", value=768, min_value=200, max_value=2160)
        else:
            width, height = resolution_options[selected_resolution]

        # Advanced options
        options = get_advanced_options()

        # Generate screenshot button
        if st.button("🎯 Generate Screenshot", key="single_url"):
            if validate_url(website_url):
                with st.spinner("📸 Capturing screenshot..."):
                    screenshot, processing_time = capture_screenshot(
                        website_url, width, height, options
                    )
                    
                    if screenshot:
                        st.success(f"✨ Screenshot captured successfully! ({processing_time:.1f}s)")
                        st.image(screenshot, use_column_width=True)
                        
                        # Download button
                        st.download_button(
                            "📥 Download Screenshot",
                            data=screenshot,
                            file_name=f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                            mime="image/png"
                        )

    with tab2:
        st.info("Batch processing feature coming soon! 🚧")

def display_footer():
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p style='color: #6c757d;'>
                <small>
                    Made with ❤️ by GitHub Copilot
                </small>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    try:
        main()
        display_footer()
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")