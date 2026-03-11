FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY tests/ ./tests/

# Expose port (if needed for web service)
EXPOSE 8000

# Run the app
CMD ["python", "app.py"]
