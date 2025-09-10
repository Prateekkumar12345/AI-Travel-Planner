# Use the official lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for some Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the working directory
COPY requirements.txt .

# Install the dependencies. We use --no-cache-dir to prevent caching, which reduces image size.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the working directory
COPY . .

# Expose port 7860 (default Gradio port)
EXPOSE 7860

# Command to run the application
# Using python -u for unbuffered output to see logs in real-time
CMD ["python", "-u", "travelAgent.py"]