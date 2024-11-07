# Use a base image with Python installed
FROM python:3.12-slim

# Install portaudio dependencies
RUN apt-get update && apt-get install -y portaudio19-dev

# Copy your requirements.txt
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy your app files
COPY . /app
WORKDIR /app

# Run your app (make sure this matches how you run Streamlit or Gradio)
CMD ["python", "app.py"]
