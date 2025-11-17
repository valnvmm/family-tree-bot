FROM python:3.11-slim

# Install system deps
RUN apt-get update && \
    apt-get install -y graphviz && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Main app folder
WORKDIR /app

# Copy entire GitHub repo into container
COPY . .

# Enter the real project folder (GitHub always nests it like this)
WORKDIR /app/family-tree-bot-main

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start the bot
CMD ["python", "bot.py"]
