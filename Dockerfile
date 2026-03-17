FROM python:3.11-slim

# Install system dependencies required for OpenCV and face processing
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set up a non-root user (Hugging Face requirement)
RUN useradd -m -u 1000 user

# Create a folder for HuggingFace to download models into (prevents permission errors)
ENV DEEPFACE_HOME="/app/.deepface"
RUN mkdir -p /app/.deepface && chown -R user:user /app

USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy requirement files and install
COPY --chown=user backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual application files
COPY --chown=user backend/ /app/backend/
COPY --chown=user frontend/ /app/frontend/

WORKDIR /app/backend

# Expose the standard 7860 port HuggingFace expects
EXPOSE 7860

# Run the FastAPI application on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
