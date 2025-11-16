import asyncpg
from config import Config

pool = None

async def init_db():
    global pool

    if pool is None:
        print("📦 Connecting to PostgreSQL...")
        pool = await asyncpg.create_pool(Config.DATABASE_URL)
        print("🟢 PostgreSQL connected.")

    # ---------- create tables if missing ----------
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            display_name TEXT
        );
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS marriages (
            user_a BIGINT REFERENCES users(user_id),
            user_b BIGINT REFERENCES users(user_id),
            married_at TIMESTAMP DEFAULT NOW(),
            PRIMARY KEY(user_a, user_b)
        );
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS relations (
            parent_id BIGINT REFERENCES users(user_id),
            child_id BIGINT REFERENCES users(user_id),
            PRIMARY KEY(parent_id, child_id)
        );
        """)

        print("📚 Tables are ready.")

# ------------------ USER FUNCTIONS ------------------
async def register_user(user_id: int, display_name: str):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (user_id, display_name)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE SET display_name = $2
        """, user_id, display_name)

async def get_user(user_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)

# ------------------ MARRIAGE ------------------
async def marry(user_a: int, user_b: int):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO marriages (user_a, user_b)
            VALUES ($1, $2)
        """, user_a, user_b)

async def divorce(user_a: int, user_b: int):
    async with pool.acquire() as conn:
        await conn.execute("""
            DELETE FROM marriages
            WHERE (user_a=$1 AND user_b=$2)
            OR (user_a=$2 AND user_b=$1)
        """, user_a, user_b)

async def get_partner(user_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
            SELECT * FROM marriages
            WHERE user_a=$1 OR user_b=$1
        """, user_id)

# ------------------ CHILDREN ------------------
async def adopt(parent_id: int, child_id: int):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO relations (parent_id, child_id)
            VALUES ($1, $2)
        """, parent_id, child_id)

async def get_children(parent_id: int):
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT child_id FROM relations WHERE parent_id=$1
        """, parent_id)
