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
    try:
        # Intentar instalar ChromeDriver
        chromedriver_autoinstaller.install()
    except Exception as e:
        st.warning(f"No se pudo instalar ChromeDriver automáticamente. Usando configuración por defecto.")
        
    options = Options()
    for option in CHROME_OPTIONS:
        options.add_argument(option)
    
    try:
        # Intentar crear el driver con la configuración por defecto
        return webdriver.Chrome(options=options)
    except Exception as e:
        st.error(f"Error al inicializar Chrome: {str(e)}")
        st.info("Asegúrate de que Chrome y ChromeDriver estén instalados en el servidor.")
        return None

@st.cache_data
def capture_screenshot(_driver, url, width, height):
    """Capture screenshot using the provided driver"""
    if _driver is None:
        st.error("No se pudo inicializar el navegador.")
        return None
        
    try:
        _driver.set_window_size(width, height)
        _driver.get(url)

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
        st.error(f"Error al capturar screenshot de {url}: {str(e)}")
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
    # Crear un buffer en memoria para el archivo ZIP
    zip_buffer = io.BytesIO()
    
    # Crear el archivo ZIP
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for url, resolutions in screenshots_data.items():
            # Obtener el dominio de la URL para usar en el nombre del archivo
            domain = urlparse(url).netloc
            
            for resolution_name, screenshot_data in resolutions.items():
                # Crear un nombre de archivo único para cada screenshot
                filename = f"{domain}_{resolution_name.split()[0].lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                
                # Añadir el screenshot al archivo ZIP
                zip_file.writestr(filename, screenshot_data)
    
    # Mover el puntero al inicio del buffer
    zip_buffer.seek(0)
    return zip_buffer.getvalue() 