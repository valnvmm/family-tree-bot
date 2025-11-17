import os

class Config:
    TOKEN = os.getenv("DISCORD_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not TOKEN:
        raise ValueError("❌ Missing TOKEN environment variable")

    if not DATABASE_URL:
        raise ValueError("❌ Missing DATABASE_URL environment variable")
