# Use the official Python image as the base
FROM python:3.9

# Set environment variable for API_URL (default value)
ENV LMSTUDIO_URL="http://localhost:1234/v1"
ENV LMSTUDIO_KEY="lm-studio"
ENV LMSTUDIO_MODEL="model-identifier"

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Python code into the container
COPY . .

# Expose port 5000 (assuming your app runs on this port)
EXPOSE 5000

# Command to run your app
CMD ["python", "main.py", "lmstudio"]
