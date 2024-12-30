import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import concurrent.futures
import hashlib
import pandas as pd
from io import StringIO
import validators
from urllib.parse import urlparse
import time
import os
from functools import lru_cache

# Configure the page
st.set_page_config(
    page_title="Website Screenshot Generator",
    page_icon="📸",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: white;
    }
    .stButton > button {
        width: 100%;
    }
    .screenshot-container {
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session states
if 'driver' not in st.session_state:
    st.session_state.driver = None
if 'cache' not in st.session_state:
    st.session_state.cache = {}


def generate_cache_key(url, width, height):
    """Generate a unique cache key based on URL and dimensions"""
    return hashlib.md5(f"{url}_{width}_{height}".encode()).hexdigest()

@lru_cache(maxsize=100)
def cache_screenshot(cache_key, screenshot):
    """Cache screenshot using Python's LRU cache"""
    return screenshot

def setup_webdriver():
    """Setup and configure WebDriver with optimized settings"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        
        # Add performance optimization arguments
        chrome_options.add_argument("--disable-javascript-harmony-shipping")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        st.error(f"Error configuring WebDriver: {str(e)}")
        return None

def validate_url(url):
    """Validate URL format and accessibility"""
    if not url:
        return False, "URL cannot be empty"
    
    if not url.strip():
        return False, "URL contains only whitespace"
    
    if not url.startswith(('http://', 'https://')):
        return False, "URL must start with http:// or https://"
    
    if not validators.url(url):
        return False, "Invalid URL format"
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]), "URL is valid"
    except Exception as e:
        return False, f"URL validation error: {str(e)}"

def wait_for_page_load(driver, timeout=10):
    """Wait for page to load using WebDriverWait instead of time.sleep"""
    try:
        # Wait for document.readyState to be 'complete'
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        
        # Wait for any loading indicators to disappear (customize selectors based on your needs)
        loading_selectors = [
            "div.loading",
            "#loader",
            ".spinner",
            "[role='progressbar']"
        ]
        
        for selector in loading_selectors:
            try:
                WebDriverWait(driver, 5).until_not(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            except:
                continue  # Skip if selector is not found
                
        # Additional wait for any dynamic content
        time.sleep(1)  # Minimal safety delay
        
    except Exception as e:
        st.warning(f"Page load wait warning: {str(e)}")

def handle_cookies_banner(driver):
    """Handle cookie banners with improved waiting mechanism"""
    try:
        # Common selectors for cookie banners and accept buttons
        cookie_selectors = [
            ("div#cookie-banner", "button#accept-cookies"),
            (".cookie-banner", ".accept-cookies"),
            ("#cookieConsent", "#acceptCookies"),
            (".cookies-notice", ".accept-cookies-button")
        ]
        
        for banner_selector, accept_selector in cookie_selectors:
            try:
                # Wait for banner with shorter timeout
                banner = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, banner_selector))
                )
                
                # Find and click accept button
                accept_button = banner.find_element(By.CSS_SELECTOR, accept_selector)
                accept_button.click()
                
                # Wait for banner to disappear
                WebDriverWait(driver, 3).until_not(
                    EC.presence_of_element_located((By.CSS_SELECTOR, banner_selector))
                )
                break  # Exit loop if successful
                
            except:
                continue  # Try next selector pair
                
    except Exception as e:
        st.warning(f"Cookie banner handling warning: {str(e)}")

def capture_full_page_screenshot(url, width, height):
    """Capture screenshot with improved error handling and caching"""
    # Check cache first
    cache_key = generate_cache_key(url, width, height)
    if cache_key in st.session_state.cache:
        return st.session_state.cache[cache_key]

    # Validate URL
    is_valid, message = validate_url(url)
    if not is_valid:
        st.error(message)
        return None

    try:
        if st.session_state.driver is None:
            st.session_state.driver = setup_webdriver()

        if not st.session_state.driver:
            return None

        # Configure window size
        st.session_state.driver.set_window_size(width, height)

        with st.status("Processing screenshot...") as status:
            # Navigate to page
            status.update(label="Navigating to page...")
            st.session_state.driver.get(url)

            # Wait for page load
            status.update(label="Waiting for page to load...")
            wait_for_page_load(st.session_state.driver)

            # Handle cookie banners
            status.update(label="Handling cookie notices...")
            handle_cookies_banner(st.session_state.driver)

            # Get page dimensions
            status.update(label="Calculating page dimensions...")
            total_height = st.session_state.driver.execute_script("""
                return Math.max(
                    document.body.scrollHeight,
                    document.documentElement.scrollHeight,
                    document.body.offsetHeight,
                    document.documentElement.offsetHeight
                );
            """)

            # Update viewport if necessary
            if total_height > height:
                st.session_state.driver.set_window_size(width, total_height)

            # Capture screenshot
            status.update(label="Capturing screenshot...")
            screenshot = st.session_state.driver.get_screenshot_as_png()

            # Cache the result
            st.session_state.cache[cache_key] = screenshot
            
            status.update(label="Done!", state="complete")
            return screenshot

    except Exception as e:
        st.error(f"Error capturing screenshot: {str(e)}")
        return None

def process_multiple_urls_concurrent(urls, width, height):
    """Process multiple URLs concurrently"""
    results = []
    total_urls = len(urls)
    
    # Create progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def process_single_url(url):
        """Helper function to process a single URL"""
        try:
            screenshot = capture_full_page_screenshot(url, width, height)
            return {
                'url': url,
                'screenshot': screenshot,
                'status': 'Success' if screenshot else 'Failed'
            }
        except Exception as e:
            return {
                'url': url,
                'screenshot': None,
                'status': f'Failed: {str(e)}'
            }

    # Use ThreadPoolExecutor for concurrent processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all URLs for processing
        future_to_url = {executor.submit(process_single_url, url): url for url in urls}
        
        # Process results as they complete
        for idx, future in enumerate(concurrent.futures.as_completed(future_to_url)):
            url = future_to_url[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    'url': url,
                    'screenshot': None,
                    'status': f'Failed: {str(e)}'
                })
            
            # Update progress
            progress = (idx + 1) / total_urls
            progress_bar.progress(progress)
            status_text.text(f"Processed {idx + 1} of {total_urls} URLs")

    status_text.text("Processing complete!")
    return results

def cleanup_resources():
    """Clean up WebDriver and cache resources"""
    try:
        if st.session_state.driver:
            st.session_state.driver.quit()
            st.session_state.driver = None
    except Exception as e:
        st.warning(f"Error during cleanup: {str(e)}")
    
    # Clear cache if it's too large (adjust threshold as needed)
    if len(st.session_state.cache) > 100:
        st.session_state.cache.clear()

def display_results(results):
    """Display screenshot results with download options"""
    successful = [r for r in results if r['status'] == 'Success']
    failed = [r for r in results if r['status'] != 'Success']
    
    st.write("### Results Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ Successfully processed: {len(successful)}")
    with col2:
        if failed:
            st.error(f"❌ Failed: {len(failed)}")
    
    if successful:
        st.write("### Screenshots")
        for result in successful:
            with st.expander(f"📸 {result['url']}"):
                st.image(result['screenshot'], use_column_width=True)
                filename = f"screenshot_{urlparse(result['url']).netloc}.png"
                st.download_button(
                    label="⬇️ Download Screenshot",
                    data=result['screenshot'],
                    file_name=filename,
                    mime="image/png"
                )
    
    if failed:
        st.write("### Failed Screenshots")
        for result in failed:
            st.error(f"❌ {result['url']}: {result['status']}")

### 5. Final Block - Main Function and App Execution
```python
def main():
    """Main application function"""
    st.title("🖼️ Website Screenshot Generator")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        width, height = get_resolution_settings()
        
        # Cache management
        if st.button("🧹 Clear Cache"):
            st.session_state.cache.clear()
            st.success("Cache cleared successfully!")
        
        # Instructions
        show_instructions()
    
    # Main content area
    tab1, tab2 = st.tabs(["📸 Single URL", "📑 Multiple URLs"])
    
    with tab1:
        with st.form(key='single_screenshot_form'):
            url = st.text_input(
                "Enter website URL",
                placeholder="https://example.com"
            )
            submit_button = st.form_submit_button("Generate Screenshot")
        
        if submit_button and url:
            screenshot = capture_full_page_screenshot(url, width, height)
            if screenshot:
                st.success("Screenshot generated successfully!")
                st.image(screenshot, use_column_width=True)
                
                filename = f"screenshot_{urlparse(url).netloc}.png"
                st.download_button(
                    label="⬇️ Download Screenshot",
                    data=screenshot,
                    file_name=filename,
                    mime="image/png"
                )
    
    with tab2:
        urls = process_multiple_urls()
        if urls and st.button("🚀 Generate All Screenshots"):
            with st.spinner("Processing multiple URLs..."):
                results = process_multiple_urls_concurrent(urls, width, height)
                display_results(results)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
    finally:
        cleanup_resources()
