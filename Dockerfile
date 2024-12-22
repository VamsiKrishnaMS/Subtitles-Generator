# Use a Python base image
FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory to /app
WORKDIR /app

# Copy all files from the project directory to /app in the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set the working directory to backend for running the app
WORKDIR /app/backend

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

COPY frontend/ /app/frontend

