import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import streamlit as st
from PIL import Image
from io import BytesIO
import zipfile
import io
from datetime import datetime
from urllib.parse import urlparse
import chromedriver_autoinstaller
from ..config.constants import CHROME_OPTIONS

def setup_webdriver():
    """Setup and return configured Chrome webdriver"""
    chromedriver_autoinstaller.install()
    options = Options()
    for option in CHROME_OPTIONS:
        options.add_argument(option)
    return webdriver.Chrome(options=options)

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
        # Abrir la imagen desde los bytes
        image = Image.open(io.BytesIO(screenshot_data))
        
        # Calcular nuevo tamaño manteniendo el aspect ratio
        # Aumentamos el tamaño para mejor calidad en pantallas de alta resolución
        max_size = (1200, 800)  # Tamaño más grande para mejor calidad
        
        # Calcular el ratio de aspecto
        aspect_ratio = image.width / image.height
        
        # Determinar el nuevo tamaño manteniendo el aspect ratio
        if aspect_ratio > max_size[0] / max_size[1]:  # Imagen más ancha
            new_width = max_size[0]
            new_height = int(new_width / aspect_ratio)
        else:  # Imagen más alta
            new_height = max_size[1]
            new_width = int(new_height * aspect_ratio)
        
        # Redimensionar usando el mejor método de interpolación
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convertir la imagen redimensionada a bytes con alta calidad
        thumb_io = io.BytesIO()
        image.save(thumb_io, format='PNG', quality=95, optimize=True)
        return thumb_io.getvalue()
    except Exception as e:
        st.error(f"Error creating thumbnail: {str(e)}")
        return None

@st.cache_data
def create_zip_file(screenshots_data):
    """Create a ZIP file containing all screenshots"""
    zip_buffer = io.BytesIO()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for url, screenshots in screenshots_data.items():
            domain = urlparse(url).netloc
            for resolution_name, screenshot in screenshots.items():
                filename = f"{domain}/{resolution_name.split()[0].lower()}.png"
                zip_file.writestr(filename, screenshot)
    
    return zip_buffer.getvalue() 