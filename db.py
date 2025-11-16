import asyncpg
from config import Config

pool = None

async def init_db():
    global pool
    print("🔧 Database setup...")
    print("📦 Connecting to PostgreSQL...")

    pool = await asyncpg.create_pool(Config.DATABASE_URL)

    async with pool.acquire() as con:
        await con.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                partner BIGINT,
                parent1 BIGINT,
                parent2 BIGINT
            );
        """)

        await con.execute("""
            CREATE TABLE IF NOT EXISTS children (
                parent BIGINT,
                child BIGINT,
                PRIMARY KEY(parent, child)
            );
        """)

    print("📚 Tables are ready.")
