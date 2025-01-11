# Bender - Screenshot Tool 📸

Una herramienta web para capturar screenshots de sitios web en diferentes resoluciones.

## Características ✨

- Captura screenshots en múltiples resoluciones
- Soporta URLs individuales y múltiples
- Resoluciones predefinidas y personalizadas
- Descarga individual o en ZIP
- Interfaz intuitiva y amigable

## Requisitos del Sistema 🛠️

### Dependencias del Sistema
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    chromium-browser \
    chromium-chromedriver \
    xvfb \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1
```

## Instalación 🚀

1. Clonar el repositorio:
```bash
git clone https://github.com/gfdiazc/bender-app-v2.git
cd bender-app-v2
```

2. Crear y activar entorno virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o
.\venv\Scripts\activate  # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso 💻

1. Iniciar la aplicación:
```bash
streamlit run app.py
```

2. Abrir en el navegador:
```
http://localhost:8501
```

## Despliegue en Producción 🌐

1. Asegurarse de tener los permisos correctos:
```bash
sudo chown -R $USER:$USER /path/to/venv
sudo chmod -R 755 /path/to/venv
```

2. Configurar variables de entorno:
```bash
export PYTHONPATH=/path/to/app:$PYTHONPATH
```

3. Ejecutar con supervisor o systemd para producción.

## Estructura del Proyecto 📁

```
bender-app-v2/
├── src/
│   ├── components/     # Componentes de la UI
│   ├── config/        # Configuraciones
│   ├── utils/         # Utilidades
│   └── styles/        # Estilos CSS
├── app.py            # Punto de entrada
├── requirements.txt  # Dependencias Python
└── packages.txt     # Dependencias del sistema
```

## Solución de Problemas 🔧

### Error de Permisos de ChromeDriver
```bash
sudo chown -R $USER:$USER /path/to/venv
sudo chmod -R 755 /path/to/venv
```

### Error de Display
```bash
export DISPLAY=:0
```

## Contribuir 🤝

1. Fork el proyecto
2. Crear una rama (`git checkout -b feature/amazing_feature`)
3. Commit los cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing_feature`)
5. Abrir un Pull Request

## Licencia 📄

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
