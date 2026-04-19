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

# Expose the port the app runs on
EXPOSE 8000

# Run the application using uvicorn natively
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
