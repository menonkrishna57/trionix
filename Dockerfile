FROM python:3.10-slim

# Install system dependencies
# ffmpeg is needed for moviepy and pydub
# libzbar0 is needed for pyzbar
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirement list first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the rest of the files into the container
COPY . .

# Expose port (Django's default)
EXPOSE 8000

# Set the working directory to where manage.py is located
WORKDIR /app/project_6_trionix

# The command that starts our application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
