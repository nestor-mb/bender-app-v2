import validators
import streamlit as st

@st.cache_data
def validate_url(url):
    """Validate URL with user feedback"""
    if not url:
        return False
    if not url.startswith(('http://', 'https://')):
        return False
    if not validators.url(url):
        return False
    return True

def validate_resolution(resolution_str):
    """Validate resolution string format"""
    try:
        width, height = map(int, resolution_str.split('x'))
        return width > 0 and height > 0
    except:
        return False 