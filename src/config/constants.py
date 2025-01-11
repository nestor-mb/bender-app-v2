# Resolution Options
RESOLUTIONS = {
    "Desktop (1920x1080)": (1920, 1080),
    "Tablet (768x1024)": (768, 1024),
    "Mobile (375x812)": (375, 812)
}

# Chrome Options
CHROME_OPTIONS = [
    "--headless",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--window-size=1920,1080",
    "--disable-extensions",
    "--disable-infobars",
    "--disable-notifications",
    "--disable-popup-blocking",
    "--start-maximized",
    "--log-level=3",
    "--ignore-certificate-errors"
]

# Page Config
PAGE_CONFIG = {
    "page_title": "Screenshot Generator Pro",
    "page_icon": "🖼️",
    "layout": "wide",
    "initial_sidebar_state": "collapsed"
} 