import os

class Config:
    TOKEN = os.getenv("TOKEN")                     # Discord Bot Token
    DATABASE_URL = os.getenv("DATABASE_URL")       # PostgreSQL URL
