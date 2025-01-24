import streamlit as st
import time
import random
from ..config.constants import RESOLUTIONS
from ..utils.validation import validate_resolution
from ..utils.screenshot import setup_webdriver, capture_screenshot

# Mensajes divertidos para el proceso de captura
LOADING_MESSAGES = [
    "🤖 Preparando los robots capturadores...",
    "📸 Ajustando el lente virtual...",
    "🎨 Mezclando los píxeles perfectos...",
    "🚀 Iniciando los motores de captura...",
    "🎯 Apuntando al objetivo...",
    "🌈 Calibrando los colores...",
    "🔍 Enfocando la página...",
    "⚡ Cargando los súper poderes...",
    "🎪 Preparando el espectáculo...",
    "🎭 Poniéndonos la máscara de captura...",
]

def process_screenshots(selected_resolutions):
    """Process screenshots for all URLs in queue"""
    st.session_state.screenshots_data = {}
    
    # Crear contenedor para la barra de progreso
    progress_placeholder = st.empty()
    message_placeholder = st.empty()
    
    driver = setup_webdriver()
    if driver is None:
        st.error("No se pudo inicializar el navegador. Por favor, verifica la instalación de Chrome y ChromeDriver en el servidor.")
        return
        
    total_tasks = len(st.session_state.urls_queue) * len(selected_resolutions)
    completed_tasks = 0
    
    try:
        for url_idx, url in enumerate(st.session_state.urls_queue):
            st.session_state.screenshots_data[url] = {}
            
            for res_idx, resolution_name in enumerate(selected_resolutions):
                # Capturar screenshot
                width, height = RESOLUTIONS[resolution_name]
                
                # Random messages to show during the capture
                loading_messages = [
                    "🤖 Preparing the capturing robots...",
                    "📸 Adjusting the virtual lens...",
                    "🎨 Mixing the perfect pixels...",
                    "🚀 Starting the capture engines...",
                    "🎯 Aiming at the target...",
                    "🌈 Calibrating the colors...",
                    "🔍 Focusing on the page...",
                    "⚡ Loading superpowers...",
                    "🎪 Preparing the show...",
                    "🎭 Putting on the capture mask..."
                ]
                
                # Iniciar la captura y medir el tiempo
                start_time = time.time()
                
                # Captura de pantalla
                screenshot = capture_screenshot(driver, url, width, height)
                
                # Calcular el tiempo que tomó la captura
                elapsed_time = time.time() - start_time
                
                # Actualizar la barra de progreso
                for i in range(10):  # 10 pasos para la barra de progreso
                    progress = (completed_tasks + (i + 1) / 10) / total_tasks
                    progress_placeholder.progress(round(progress, 2))
                    time.sleep(elapsed_time / 10)  # Sincronizar con el tiempo de captura
                    
                    # Cambiar el mensaje de carga
                    message_placeholder.markdown(f"<p style='text-align: center'>{random.choice(loading_messages)}</p>", unsafe_allow_html=True)
                
                if screenshot:
                    st.session_state.screenshots_data[url][resolution_name] = screenshot
                completed_tasks += 1
            
            if completed_tasks > 0:
                # Mostrar progreso final
                progress_placeholder.progress(1.0)
                message_placeholder.markdown("<p style='text-align: center'>Todas las capturas han sido procesadas exitosamente</p>", unsafe_allow_html=True)
                
                # Efectos de celebración
                st.balloons()
                st.success("¡Todas las capturas han sido completadas con éxito! 🎉")
                
                st.session_state.show_results = True
                time.sleep(1)
                st.rerun()
    
    finally:
        if driver:
            driver.quit()

def queue_manager_section():
    """Component for managing URL queue and screenshot settings"""
    if not st.session_state.urls_queue:
        return

    with st.container():
        st.markdown("<div class='section-container'>", unsafe_allow_html=True)
        st.subheader("URL Queue")
        
        with st.expander("View Queue", expanded=True):
            for idx, url in enumerate(st.session_state.urls_queue):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"{idx + 1}. {url}")
                with col2:
                    if st.button("🗑️", key=f"remove_{idx}", type="secondary", help="Remove URL"):
                        st.session_state.urls_queue.pop(idx)
                        st.rerun()
        
            if st.button("Clear Queue", type="secondary", key="clear_queue", help="Remove all URLs", use_container_width=True):
                st.session_state.urls_queue = []
                st.rerun()
        
        # Resolution Selection
        st.subheader("Screenshot Settings")
        selected_resolutions = st.multiselect(
            "Select Resolutions",
            options=list(RESOLUTIONS.keys()),
            default=["Desktop (1920x1080)"],
            help="Choose one or more resolutions for your screenshots"
        )
        
        # Custom Resolution
        custom_resolution = st.text_input(
            "Custom Resolution (optional)",
            placeholder="e.g., 1200x800",
            help="Enter a custom resolution in WIDTHxHEIGHT format"
        )
        
        if custom_resolution and validate_resolution(custom_resolution):
            width, height = map(int, custom_resolution.split('x'))
            resolution_name = f"Custom ({width}x{height})"
            RESOLUTIONS[resolution_name] = (width, height)
            if resolution_name not in selected_resolutions:
                selected_resolutions.append(resolution_name)
        elif custom_resolution:
            st.error("Invalid resolution format. Use WIDTHxHEIGHT (e.g., 1200x800)")
        
        if st.button("🚀 Generate Screenshots", type="primary", disabled=not selected_resolutions, use_container_width=True):
            process_screenshots(selected_resolutions)
        
        st.markdown("</div>", unsafe_allow_html=True) 