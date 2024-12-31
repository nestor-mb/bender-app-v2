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
import io
import base64
from PIL import Image
from io import BytesIO
import pyperclip  # You'll need to install this: pip install pyperclip

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
    """Capture screenshot with improved cookie banner handling"""
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

            # Enhanced cookie banner handling
            try:
                # Extended list of common cookie acceptance button patterns
                cookie_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, """
                        //button[
                            contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept') or 
                            contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agree') or 
                            contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'aceptar') or 
                            contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'aceitar') or 
                            contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'aceptar todas') or 
                            contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept all') or 
                            contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'allow all')
                        ] | 
                        //div[
                            contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept') or 
                            contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agree')
                        ]
                    """))
                )
                driver.execute_script("arguments[0].click();", cookie_button)
                time.sleep(2)  # Wait for banner to disappear
            except Exception:
                # Try alternative methods if the first attempt fails
                try:
                    # Look for iframes that might contain cookie banners
                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    for iframe in iframes:
                        try:
                            driver.switch_to.frame(iframe)
                            cookie_button = driver.find_element(By.XPATH, """
                                //*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept') or 
                                   contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agree')]
                            """)
                            driver.execute_script("arguments[0].click();", cookie_button)
                            driver.switch_to.default_content()
                            time.sleep(2)
                            break
                        except:
                            driver.switch_to.default_content()
                except:
                    pass  # Continue if no cookie banner is found

            # Adjust window size for full page if requested
            if options.get('full_page', True):
                total_height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
                driver.set_window_size(width, total_height)
                time.sleep(1)  # Wait for resize

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

def format_filename(base_name, format_option, timestamp):
    """Format filename based on user selection"""
    if format_option == "Date_Time":
        return f"{base_name}_{timestamp}"
    elif format_option == "Unix_Timestamp":
        return f"{base_name}_{int(datetime.now().timestamp())}"
    elif format_option == "Custom":
        return st.text_input("Enter custom filename", value=base_name)
    return base_name

def create_zip_file(screenshots, url, format_option):
    """Create a ZIP file containing all screenshots"""
    zip_buffer = io.BytesIO()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for resolution_name, screenshot_data in screenshots.items():
            base_name = f"screenshot_{resolution_name.split()[0].lower()}"
            filename = format_filename(base_name, format_option, timestamp) + ".png"
            zip_file.writestr(filename, screenshot_data)
    
    return zip_buffer.getvalue()

def copy_to_clipboard(image_data):
    """Copy image data to clipboard"""
    try:
        import pyperclip
        from PIL import Image
        from io import BytesIO
        
        # Convert PNG data to base64
        image_b64 = base64.b64encode(image_data).decode()
        pyperclip.copy(f"data:image/png;base64,{image_b64}")
        return True
    except Exception as e:
        st.error(f"Failed to copy to clipboard: {str(e)}")
        return False

def create_thumbnail(image_data, max_size=(150, 150)):
    """Create a thumbnail from image data"""
    try:
        image = Image.open(BytesIO(image_data))
        image.thumbnail(max_size)
        thumb_buffer = BytesIO()
        image.save(thumb_buffer, format='PNG')
        return thumb_buffer.getvalue()
    except Exception as e:
        st.error(f"Failed to create thumbnail: {str(e)}")
        return None

def main():
    st.title("🖼️ Website Screenshot Generator Pro")
    
    # Main content tabs
    tab1, tab2 = st.tabs(["📸 Single URL", "📑 Batch Processing"])

    with tab1:
        website_url = st.text_input(
            "Enter website URL",
            placeholder="https://example.com"
        )

        # Resolution selection with multiple choice
        st.subheader("Select Screenshot Resolutions")
        
        resolution_options = {
            "Desktop (1920x1080)": (1920, 1080),
            "Tablet (768x1024)": (768, 1024),
            "Mobile (375x812)": (375, 812)
        }
        
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_resolutions = st.multiselect(
                "Choose one or more resolutions:",
                options=list(resolution_options.keys()),
                default=["Desktop (1920x1080)"],
                help="Select multiple resolutions to generate screenshots for each"
            )
        
        # Advanced options in a cleaner layout
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
                filename_format = st.selectbox(
                    "Filename Format",
                    ["Date_Time", "Unix_Timestamp", "Custom"]
                )

        # Generate screenshots button
        if st.button("🎯 Generate Screenshots", key="single_url"):
            if not selected_resolutions:
                st.warning("⚠️ Please select at least one resolution")
            elif validate_url(website_url):
                screenshots_data = {}
                
                # Progress bar with status
                progress_text = "Generating screenshots..."
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Generate screenshots
                for idx, resolution_name in enumerate(selected_resolutions):
                    status_text.text(f"Capturing {resolution_name}...")
                    width, height = resolution_options[resolution_name]
                    screenshot, processing_time = capture_screenshot(
                        website_url, width, height, 
                        {"wait_time": wait_time, "full_page": full_page}
                    )
                    
                    if screenshot:
                        screenshots_data[resolution_name] = screenshot
                    
                    # Update progress
                    progress = (idx + 1) / len(selected_resolutions)
                    progress_bar.progress(progress)
                
                if screenshots_data:
                    status_text.text("✨ All screenshots captured successfully!")
                    
                    # Download options
                    st.subheader("Download Options")
                    download_option = st.radio(
                        "Select download format:",
                        ["Individual Files", "ZIP Archive", "Copy to Clipboard"],
                        horizontal=True
                    )
                    
                    # Thumbnail gallery
                    st.subheader("Screenshots Preview")
                    thumbnail_cols = st.columns(len(screenshots_data))
                    
                    for idx, (resolution_name, screenshot) in enumerate(screenshots_data.items()):
                        with thumbnail_cols[idx]:
                            thumbnail = create_thumbnail(screenshot)
                            if thumbnail:
                                st.image(thumbnail, caption=resolution_name)
                                if st.button(f"Show {resolution_name}", key=f"show_{idx}"):
                                    with st.expander(f"📸 {resolution_name} Full Size", expanded=True):
                                        st.image(screenshot, use_container_width=True)
                    
                    # Download section
                    st.subheader("Download Section")
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    
                    if download_option == "Individual Files":
                        for resolution_name, screenshot in screenshots_data.items():
                            base_name = f"screenshot_{resolution_name.split()[0].lower()}"
                            filename = format_filename(base_name, filename_format, timestamp) + ".png"
                            
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.download_button(
                                    f"📥 Download {resolution_name}",
                                    data=screenshot,
                                    file_name=filename,
                                    mime="image/png"
                                )
                            with col2:
                                if st.button(f"📋 Copy {resolution_name}", key=f"copy_{resolution_name}"):
                                    if copy_to_clipboard(screenshot):
                                        st.success(f"✅ {resolution_name} copied to clipboard!")
                    
                    elif download_option == "ZIP Archive":
                        zip_data = create_zip_file(screenshots_data, website_url, filename_format)
                        st.download_button(
                            "📦 Download All Screenshots (ZIP)",
                            data=zip_data,
                            file_name=f"screenshots_{timestamp}.zip",
                            mime="application/zip"
                        )
                    
                    else:  # Copy to Clipboard
                        for resolution_name, screenshot in screenshots_data.items():
                            if st.button(f"📋 Copy {resolution_name} to Clipboard", key=f"clipboard_{resolution_name}"):
                                if copy_to_clipboard(screenshot):
                                    st.success(f"✅ {resolution_name} copied to clipboard!")

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
    main()
    display_footer()