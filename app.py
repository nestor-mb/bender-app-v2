import streamlit as st
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import validators
from urllib.parse import urlparse
import concurrent.futures

# Configure the page
st.set_page_config(
    page_title="Website Screenshot Generator",
    page_icon="📸",
    layout="wide"
)

# Constants for resolutions
RESOLUTIONS = {
    "Desktop (1920x1080)": (1920, 1080),
    "Tablet (768x1024)": (768, 1024),
    "Mobile (375x812)": (375, 812)
}

def setup_webdriver():
    """Setup and configure Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        st.error(f"Error configuring WebDriver: {str(e)}")
        return None

def capture_screenshot(url, width, height):
    """Capture screenshot of a URL"""
    driver = setup_webdriver()
    if not driver:
        return None
    
    try:
        driver.set_window_size(width, height)
        driver.get(url)

        # Wait for page load
        time.sleep(3)

        # Handle cookies pop-up if present
        try:
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, 
                    "//button[contains(text(), 'Aceptar') or "
                    "contains(text(), 'Aceptar todas') or "
                    "contains(text(), 'Agree') or "
                    "contains(text(), 'Accept')]"))
            )
            cookie_button.click()
            time.sleep(2)
        except Exception:
            pass

        # Adjust window size for full page
        total_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(width, total_height)
        
        # Take screenshot
        screenshot = driver.get_screenshot_as_png()
        return screenshot

    except Exception as e:
        st.error(f"Error capturing screenshot: {str(e)}")
        return None
    finally:
        driver.quit()

def validate_url(url):
    """Validate URL format"""
    if not url:
        return False
    if not url.startswith(('http://', 'https://')):
        return False
    return validators.url(url)

def main():
    st.title("🖼️ Website Screenshot Generator")

    # Sidebar for resolution selection
    with st.sidebar:
        st.header("📏 Resolution Settings")
        selected_resolution = st.selectbox(
            "Choose Device Resolution",
            list(RESOLUTIONS.keys())
        )
        width, height = RESOLUTIONS[selected_resolution]
        st.info(f"Selected resolution: {width}x{height}")

    # Main content area
    tab1, tab2 = st.tabs(["Single URL", "Multiple URLs"])

    with tab1:
        url = st.text_input("Enter website URL", placeholder="https://example.com")
        if st.button("Generate Screenshot") and url:
            if validate_url(url):
                with st.spinner("Generating screenshot..."):
                    screenshot = capture_screenshot(url, width, height)
                    if screenshot:
                        st.success("Screenshot generated successfully!")
                        st.image(screenshot)
                        
                        # Download button
                        filename = f"screenshot_{urlparse(url).netloc}.png"
                        st.download_button(
                            label="Download Screenshot",
                            data=screenshot,
                            file_name=filename,
                            mime="image/png"
                        )
            else:
                st.error("Please enter a valid URL")

    with tab2:
        uploaded_file = st.file_uploader("Upload a CSV or TXT file with URLs (one per line)")
        if uploaded_file:
            content = uploaded_file.getvalue().decode()
            urls = [url.strip() for url in content.split('\n') if url.strip()]
            
            if st.button("Process All URLs"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                for idx, url in enumerate(urls):
                    if validate_url(url):
                        status_text.text(f"Processing {url}...")
                        screenshot = capture_screenshot(url, width, height)
                        
                        if screenshot:
                            results.append({
                                "URL": url,
                                "Status": "Success",
                                "Screenshot": screenshot
                            })
                        else:
                            results.append({
                                "URL": url,
                                "Status": "Failed",
                                "Screenshot": None
                            })
                    else:
                        results.append({
                            "URL": url,
                            "Status": "Invalid URL",
                            "Screenshot": None
                        })
                    
                    progress_bar.progress((idx + 1) / len(urls))
                
                # Display results
                st.write("### Results")
                for result in results:
                    with st.expander(f"📸 {result['URL']}"):
                        st.write(f"Status: {result['Status']}")
                        if result['Screenshot']:
                            st.image(result['Screenshot'])
                            filename = f"screenshot_{urlparse(result['URL']).netloc}.png"
                            st.download_button(
                                label="Download Screenshot",
                                data=result['Screenshot'],
                                file_name=filename,
                                mime="image/png"
                            )

if __name__ == "__main__":
    main()
