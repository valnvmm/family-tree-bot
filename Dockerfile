FROM python:3.11-slim

# Install system deps
RUN apt-get update && \
    apt-get install -y graphviz && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create main folder
WORKDIR /app

# Copy repo contents into /app
COPY . .

# Move into the actual project folder (GitHub -> ZIP -> foldername-main)
WORKDIR /app/family-tree-bot-main

# Install Python dependencies INSIDE this folder
RUN pip install --no-cache-dir -r requirements.txt

# Start the bot
CMD ["python", "bot.py"]
