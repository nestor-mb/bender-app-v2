import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configuración de la página
st.set_page_config(
    page_title="Generador de Capturas de Pantalla de Sitios Web",
    page_icon="📸",
    layout="wide"
)

# Inicializar el estado de la sesión para el driver
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
        chrome_options.binary_location = "/usr/bin/chromium-browser"  # Specify the Chromium binary location
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        st.error(f"Error al configurar WebDriver: {str(e)}")
        return None

def capture_screenshot(url, width=1920, height=1080):
    try:
        if st.session_state.driver is None:
            st.session_state.driver = setup_webdriver()
            
        if not st.session_state.driver:
            return None

        # Establecer el tamaño de la ventana
        st.session_state.driver.set_window_size(width, height)
        
        # Navegar a la URL
        st.session_state.driver.get(url)
        
        # Esperar a que la página cargue
        time.sleep(3)
        
        # Tomar captura de pantalla
        screenshot = st.session_state.driver.get_screenshot_as_png()
        return screenshot

    except Exception as e:
        st.error(f"Error al capturar la captura de pantalla: {str(e)}")
        return None

def main():
    st.title("Generador de Capturas de Pantalla de Sitios Web")
    st.write("Genera capturas de pantalla de cualquier sitio web")

    # Entrada de URL
    url = st.text_input(
        "Ingrese la URL del sitio web",
        placeholder="https://ejemplo.com"
    )

    # Selección de resolución
    resolutions = {
        "Escritorio (1920x1080)": (1920, 1080),
        "Tablet (768x1024)": (768, 1024),
        "Móvil (375x812)": (375, 812)
    }
    
    resolution = st.selectbox(
        "Seleccione la resolución",
        list(resolutions.keys())
    )

    if st.button("Generar Captura"):
        if not url:
            st.error("Por favor, ingrese una URL")
            return

        if not url.startswith(('http://', 'https://')):
            st.error("Por favor, ingrese una URL válida que comience con http:// o https://")
            return

        with st.spinner("Generando captura de pantalla..."):
            width, height = resolutions[resolution]
            screenshot = capture_screenshot(url, width, height)
            
            if screenshot:
                st.success("¡Captura de pantalla generada con éxito!")
                st.image(screenshot, use_column_width=True)
                
                # Botón de descarga
                filename = f"captura_{width}x{height}.png"
                st.download_button(
                    label="Descargar Captura",
                    data=screenshot,
                    file_name=filename,
                    mime="image/png"
                )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Ocurrió un error: {str(e)}")
    finally:
        # Limpiar el driver cuando se cierra la aplicación
        if st.session_state.driver:
            st.session_state.driver.quit()
