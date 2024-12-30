# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Install system dependencies including python3-distutils
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    python3-distutils \
    python3-dev \
    build-essential \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Expose port
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "app.py"]
