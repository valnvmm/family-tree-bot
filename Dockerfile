FROM python:3.11-slim

# Install system deps
RUN apt-get update && \
    apt-get install -y graphviz && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create main folder inside container
WORKDIR /app

# Copy GitHub repo into /app
COPY . .

# Now move into the actual project folder (GitHub ZIP always wraps it)
WORKDIR /app/family-tree-bot-main

# Install Python dependencies from this folder
RUN pip install --no-cache-dir -r requirements.txt

# Start your bot
CMD ["python", "bot.py"]
