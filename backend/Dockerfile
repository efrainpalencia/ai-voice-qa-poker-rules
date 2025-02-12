# Use Python image as base
FROM python:3.10

# Set working directory
WORKDIR /app

# Install system dependencies (including FFmpeg)
RUN apt-get update && apt-get install -y ffmpeg

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose port (if needed)
EXPOSE 5000

# Command to run Flask app
CMD ["python", "server.py"]
