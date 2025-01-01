import streamlit as st
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import validators
from datetime import datetime
import zipfile
from urllib.parse import urlparse
import io
import base64
from PIL import Image
from io import BytesIO
import pyperclip
import os
import json

# Page Configuration
st.set_page_config(
    page_title="Screenshot Generator Pro",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    /* Light mode styles */
    .main {
        padding: 2rem;
    }
    
    h1 {
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .stTextInput > div > div > input {
        border-radius: 0.5rem;
    }
    
    .stSelectbox > div > div > div {
        border-radius: 0.5rem;
    }
    
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
    
    .stProgress > div > div {
        background-color: #1E88E5;
    }
    
    .stAlert {
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Chrome Options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

# Resolution Options
RESOLUTIONS = {
    "Desktop (1920x1080)": (1920, 1080),
    "Tablet (768x1024)": (768, 1024),
    "Mobile (375x812)": (375, 812)
}

# Helper Functions
@st.cache_data
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

@st.cache_data
def capture_screenshot(_driver, url, width, height):
    """Capture screenshot using the provided driver"""
    _driver.set_window_size(width, height)
    _driver.get(url)

    try:
        # Wait for the page to load fully
        time.sleep(3)

        # Handle cookies pop-up if present
        try:
            cookie_button = WebDriverWait(_driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceptar') or contains(text(), 'Aceptar todas') or contains(text(), 'Agree') or contains(text(), 'Accept')]"))
            )
            cookie_button.click()
            time.sleep(2)  # Wait for the pop-up to disappear
        except Exception:
            pass  # No cookie pop-up found, continue

        # Adjust window size for full page
        total_height = _driver.execute_script("return document.body.scrollHeight")
        _driver.set_window_size(width, total_height)
        screenshot = _driver.get_screenshot_as_png()
        return screenshot
    except Exception as e:
        st.error(f"Error capturing screenshot for {url}: {e}")
        return None

@st.cache_data
def create_thumbnail(screenshot_data):
    """Create a thumbnail from screenshot data"""
    try:
        image = Image.open(BytesIO(screenshot_data))
        image.thumbnail((300, 300))
        return image
    except Exception as e:
        st.error(f"Failed to create thumbnail: {str(e)}")
        return None

@st.cache_data
def create_zip_file(screenshots, url, format_option):
    """Create a ZIP file containing all screenshots"""
    zip_buffer = io.BytesIO()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for resolution_name, screenshot_data in screenshots.items():
            filename = f"screenshot_{resolution_name.split()[0].lower()}_{timestamp}.png"
            zip_file.writestr(filename, screenshot_data)
    
    return zip_buffer.getvalue()

@st.cache_data
def copy_to_clipboard(image_data):
    """Copy image data to clipboard"""
    try:
        image_b64 = base64.b64encode(image_data).decode()
        html = f'<img src="data:image/png;base64,{image_b64}">'
        pyperclip.copy(html)
        return True
    except Exception as e:
        st.error(f"Failed to copy to clipboard: {str(e)}")
        return False

# Main Application
def main():
    st.title("🖼️ Website Screenshot Generator Pro")
    
    # Initialize session state
    if 'screenshots_data' not in st.session_state:
        st.session_state.screenshots_data = {}
    if 'batch_urls' not in st.session_state:
        st.session_state.batch_urls = []
    
    # Sidebar for Navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio("Go to", ["Single URL", "Multiple URLs", "Help", "Feedback"])
    
    
    # Help Section
    if page == "Help":
        with st.expander("❓ Help"):
            st.write("### How to Use This App")
            st.write("1. Enter a URL or upload a file with multiple URLs.")
            st.write("2. Select the resolutions you want to capture.")
            st.write("3. Click 'Generate Screenshots' to start the process.")
            st.write("4. Preview, download, or share your screenshots.")
    
    # Feedback Form
    if page == "Feedback":
        with st.expander("💬 Feedback"):
            feedback = st.text_area("Share your feedback or report an issue:")
            if st.button("Submit Feedback", key="submit_feedback"):
                with open("feedback.txt", "a") as f:
                    f.write(f"{datetime.now()}: {feedback}\n")
                st.success("Thank you for your feedback!")
    
    # Single URL Tab
    if page == "Single URL":
        website_url = st.text_input("Enter website URL", placeholder="https://example.com", help="Enter the URL of the website you want to capture.")

        # Resolution selection
        st.subheader("Select Screenshot Resolutions")
        selected_resolutions = st.multiselect(
            "Choose one or more resolutions:",
            options=list(RESOLUTIONS.keys()),
            default=["Desktop (1920x1080)"],
            key="single_resolutions",
            help="Select the resolutions for which you want to capture screenshots."
        )

        # Custom resolution input
        custom_resolution = st.text_input("Enter custom resolution (e.g., 1200x800)", help="Enter a custom resolution in the format 'WIDTHxHEIGHT'.")
        if custom_resolution:
            try:
                width, height = map(int, custom_resolution.split('x'))
                RESOLUTIONS[f"Custom ({width}x{height})"] = (width, height)
            except:
                st.error("Invalid resolution format. Use 'WIDTHxHEIGHT' (e.g., 1200x800).")

        if st.button("🎯 Generate Screenshots", key="single_url"):
            if not selected_resolutions:
                st.warning("⚠️ Please select at least one resolution")
            elif validate_url(website_url):
                screenshots_data = {}
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                driver = webdriver.Chrome(options=chrome_options)
                
                for idx, resolution_name in enumerate(selected_resolutions):
                    status_text.text(f"Capturing {resolution_name}...")
                    width, height = RESOLUTIONS[resolution_name]
                    screenshot = capture_screenshot(driver, website_url, width, height)
                    
                    if screenshot:
                        screenshots_data[resolution_name] = screenshot
                    
                    progress_bar.progress((idx + 1) / len(selected_resolutions))
                
                driver.quit()
                
                if screenshots_data:
                    status_text.text("✨ All screenshots captured!")
                    st.toast("Screenshots captured successfully!", icon="🎉")
                    
                    st.subheader("Download Options")
                    download_option = st.radio(
                        "Select format:",
                        ["Individual Files", "ZIP Archive", "Copy to Clipboard"],
                        key="single_download_option",
                        horizontal=True
                    )
                    
                    st.subheader("Screenshots Preview")
                    cols = st.columns(len(screenshots_data))
                    
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    
                    for idx, (resolution_name, screenshot) in enumerate(screenshots_data.items()):
                        with cols[idx]:
                            if thumbnail := create_thumbnail(screenshot):
                                st.image(thumbnail, caption=resolution_name)
                                
                                if download_option == "Individual Files":
                                    filename = f"screenshot_{resolution_name.split()[0].lower()}_{timestamp}.png"
                                    st.download_button(
                                        "📥 Download",
                                        data=screenshot,
                                        file_name=filename,
                                        mime="image/png",
                                        key=f"single_download_{idx}"
                                    )
                                elif download_option == "Copy to Clipboard":
                                    if st.button("📋 Copy", key=f"single_copy_{idx}"):
                                        if copy_to_clipboard(screenshot):
                                            st.success("✅ Copied!")
                    
                    if download_option == "ZIP Archive":
                        zip_data = create_zip_file(screenshots_data, website_url, "Date_Time")
                        st.download_button(
                            "📦 Download All (ZIP)",
                            data=zip_data,
                            file_name=f"screenshots_{timestamp}.zip",
                            mime="application/zip",
                            key="single_zip"
                        )

    # Multiple URLs Tab
    if page == "Multiple URLs":
        
        # Option 1: Upload a file with URLs
        st.subheader("Option 1: Upload a File")
        uploaded_file = st.file_uploader("Upload a CSV or text file with URLs", type=["csv", "txt"], help="Upload a file containing one URL per line.")
        
        # Option 2: Manually enter URLs
        st.subheader("Option 2: Manually Enter URLs")
        manual_urls = st.text_area("Paste URLs here (one per line):", placeholder="https://example.com\nhttps://another-example.com", help="Paste your URLs here, one per line.")
        st.subheader("Multiple URLs Processing")
        
        # Add URLs to the queue
        if st.button("➕ Add URLs to Queue", key="add_urls"):
            urls = []
            if uploaded_file:
                urls.extend(uploaded_file.read().decode("utf-8").splitlines())
            if manual_urls:
                urls.extend([url.strip() for url in manual_urls.split('\n') if url.strip()])
            
            valid_urls = [url for url in urls if validate_url(url)]
            st.session_state.batch_urls.extend(valid_urls)
            
            if valid_urls:
                st.success(f"✅ Added {len(valid_urls)} URLs to the queue!")
                if len(urls) > len(valid_urls):
                    st.warning(f"⚠️ {len(urls) - len(valid_urls)} invalid URLs were skipped.")
            else:
                st.warning("⚠️ No URLs were added. Please upload a file or enter URLs manually.")
        
        # Display URLs in the queue
        if st.session_state.batch_urls:
            st.write(f"**{len(st.session_state.batch_urls)} URLs in queue**")
            for idx, url in enumerate(st.session_state.batch_urls):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"{idx + 1}. {url}")
                with col2:
                    if st.button("🗑️", key=f"remove_{idx}"):
                        st.session_state.batch_urls.pop(idx)
                        st.rerun()
            
            # Clear Queue Button
            if st.button("🧹 Clear Queue", key="clear_queue"):
                st.session_state.batch_urls = []
                st.rerun()
            
            # Resolution selection for batch processing
            st.subheader("Select Screenshot Resolutions")
            selected_resolutions = st.multiselect(
                "Choose resolutions:",
                options=list(RESOLUTIONS.keys()),
                default=["Desktop (1920x1080)"],
                key="batch_resolutions",
                help="Select the resolutions for which you want to capture screenshots."
            )
            
            if st.button("🚀 Process Queue", key="process_batch"):
                if not selected_resolutions:
                    st.warning("⚠️ Please select at least one resolution")
                else:
                    st.session_state.screenshots_data = {}
                    total_tasks = len(st.session_state.batch_urls) * len(selected_resolutions)
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    driver = webdriver.Chrome(options=chrome_options)
                    
                    for url_idx, url in enumerate(st.session_state.batch_urls):
                        st.session_state.screenshots_data[url] = {}
                        status_text.text(f"Processing URL {url_idx + 1}/{len(st.session_state.batch_urls)}: {url}")
                        
                        for res_idx, resolution_name in enumerate(selected_resolutions):
                            width, height = RESOLUTIONS[resolution_name]
                            status_text.text(f"Capturing {resolution_name} for {url}")
                            
                            screenshot = capture_screenshot(driver, url, width, height)
                            
                            if screenshot:
                                st.session_state.screenshots_data[url][resolution_name] = screenshot
                            
                            progress = (url_idx * len(selected_resolutions) + res_idx + 1) / total_tasks
                            progress_bar.progress(progress)
                    
                    driver.quit()
                    status_text.text("✨ Batch processing completed!")
                    st.toast("Batch processing completed!", icon="🎉")
            
            # Display batch results
            if st.session_state.screenshots_data:
                st.subheader("Results")
                
                download_option = st.radio(
                    "Select download format:",
                    ["Individual Files", "ZIP Archive"],
                    key="batch_download_option",
                    horizontal=True
                )
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                if download_option == "ZIP Archive":
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for url, screenshots in st.session_state.screenshots_data.items():
                            domain = urlparse(url).netloc
                            for resolution_name, screenshot in screenshots.items():
                                filename = f"{domain}/{resolution_name.split()[0].lower()}.png"
                                zip_file.writestr(filename, screenshot)
                    
                    st.download_button(
                        "📦 Download All Screenshots (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name=f"batch_screenshots_{timestamp}.zip",
                        mime="application/zip",
                        key="batch_zip"
                    )
                
                for url in st.session_state.batch_urls:
                    if url in st.session_state.screenshots_data:
                        with st.expander(f"📸 {url}"):
                            screenshots = st.session_state.screenshots_data[url]
                            cols = st.columns(len(screenshots))
                            
                            for idx, (resolution_name, screenshot) in enumerate(screenshots.items()):
                                with cols[idx]:
                                    if thumbnail := create_thumbnail(screenshot):
                                        st.image(thumbnail, caption=resolution_name)
                                        
                                        if download_option == "Individual Files":
                                            domain = urlparse(url).netloc
                                            filename = f"{domain}_{resolution_name.split()[0].lower()}_{timestamp}.png"
                                            st.download_button(
                                                "📥 Download",
                                                data=screenshot,
                                                file_name=filename,
                                                mime="image/png",
                                                key=f"batch_download_{url}_{idx}"
                                            )

    # Clear All Feature
    if st.sidebar.button("🧹 Clear All", key="clear_all"):
        st.session_state.screenshots_data = {}
        st.session_state.batch_urls = []
        st.rerun()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")