# Use the official, lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements first (this makes Docker building much faster!)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Run the application using Gunicorn (Production standard!)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]