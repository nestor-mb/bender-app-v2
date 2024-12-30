import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

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
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for the driver
if 'driver' not in st.session_state:
    st.session_state.driver = None

def setup_webdriver():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--window-size=1920x1080")  # Set a large window size for full-page screenshot

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        st.error(f"Error configuring WebDriver: {str(e)}")
        return None

def handle_cookies_banner(driver):
    try:
        # Example selectors for the cookies banner and accept button
        cookies_banner_selector = "div#cookie-banner"  # Update this selector based on the actual site
        accept_button_selector = "button#accept-cookies"  # Update this selector based on the actual site
        
        # Wait for the cookies banner to appear
        time.sleep(2)
        banner = driver.find_element_by_css_selector(cookies_banner_selector)
        accept_button = driver.find_element_by_css_selector(accept_button_selector)
        
        if banner and accept_button:
            accept_button.click()
            time.sleep(1)  # Wait for the banner to disappear
    except Exception as e:
        st.warning(f"Could not handle cookies banner: {str(e)}")

def capture_full_page_screenshot(url):
    try:
        if st.session_state.driver is None:
            st.session_state.driver = setup_webdriver()
            
        if not st.session_state.driver:
            return None

        # Navigate to the URL
        st.session_state.driver.get(url)
        
        # Handle cookies banner
        handle_cookies_banner(st.session_state.driver)
        
        # Wait for the page to load
        time.sleep(3)
        
        # Get the total height of the page
        total_height = st.session_state.driver.execute_script("return document.body.scrollHeight")
        st.session_state.driver.set_window_size(1920, total_height)

        # Take a screenshot
        screenshot = st.session_state.driver.get_screenshot_as_png()
        return screenshot

    except Exception as e:
        st.error(f"Error capturing screenshot: {str(e)}")
        return None

def main():
    st.title("Website Screenshot Generator")
    st.write("Generate full-page screenshots of any website quickly and easily.")

    with st.form(key='screenshot_form'):
        url = st.text_input("Enter the website URL", placeholder="https://example.com")
        resolution = st.selectbox("Select resolution", ["Desktop (1920x1080)", "Tablet (768x1024)", "Mobile (375x812)"])
        submit_button = st.form_submit_button(label='Generate Screenshot')

    if submit_button:
        if not url:
            st.error("Please enter a URL.")
            return

        if not url.startswith(('http://', 'https://')):
            st.error("Please enter a valid URL starting with http:// or https://")
            return

        with st.spinner("Generating full-page screenshot..."):
            screenshot = capture_full_page_screenshot(url)
            
            if screenshot:
                st.success("Screenshot generated successfully!")
                st.image(screenshot, use_column_width=True)
                
                filename = "full_page_screenshot.png"
                st.download_button(
                    label="Download Screenshot",
                    data=screenshot,
                    file_name=filename,
                    mime="image/png"
                )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    finally:
        if st.session_state.driver:
            st.session_state.driver.quit()
