# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# We use opencv-python-headless, so no extra apt-get dependencies are required
# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the application using the dynamic PORT provided by the environment (Render)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
