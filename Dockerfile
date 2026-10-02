# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data /app/uploads

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Set environment variables
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Create Streamlit config directory
RUN mkdir -p ~/.streamlit

# Create Streamlit config file
RUN echo "\
[theme]\n\
primaryColor='#1f77b4'\n\
backgroundColor='#ffffff'\n\
secondaryBackgroundColor='#f0f2f6'\n\
textColor='#262730'\n\
[server]\n\
headless=true\n\
port=8501\n\
" > ~/.streamlit/config.toml

# Run the application
CMD ["streamlit", "run", "app/streamlit_app.py"]
