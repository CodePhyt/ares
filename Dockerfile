FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download German spaCy model for Presidio
RUN python -m spacy download de_core_news_sm

# Copy application code
COPY src/ /app/src/
COPY .env.example /app/.env

# Create necessary directories
RUN mkdir -p /app/data /app/chroma_db /app/uploads

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
