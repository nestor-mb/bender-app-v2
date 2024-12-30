FROM python:3.9-slim

# Install system dependencies
RUN apt-get update -q && \
    apt-get install -y \
    chromium-chromedriver \
    chromium \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy chromedriver to the correct location
RUN cp /usr/lib/chromium/chromedriver /usr/bin

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Expose port
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "app.py"]
