"""Constants for the application"""

# Available resolutions
RESOLUTIONS = {
    "Mobile (375x667)": (375, 667),
    "Tablet (768x1024)": (768, 1024),
    "Desktop (1920x1080)": (1920, 1080),
}

# Chrome options for webdriver
CHROME_OPTIONS = [
    "--headless=new",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-extensions",
    "--disable-infobars",
    "--disable-notifications",
    "--disable-popup-blocking",
    "--start-maximized",
    "--log-level=3",
    "--ignore-certificate-errors",
    "--window-size=1920,1080",
]

# Page configuration
PAGE_CONFIG = {
    "page_title": "Bender - Screenshot Tool",
    "page_icon": "📸",
    "layout": "centered",
    "initial_sidebar_state": "collapsed",
    "menu_items": None
} 