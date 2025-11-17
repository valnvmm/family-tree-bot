import os

class Config:
    TOKEN = os.getenv("DISCORD_TOKEN")                     # Discord Bot Token
    DATABASE_URL = os.getenv("DATABASE_URL")       # PostgreSQL URL
