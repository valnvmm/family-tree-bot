import asyncpg
from config import Config

pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(Config.DATABASE_URL)
    print("✅ PostgreSQL connected.")

async def fetch(query, *args):
    async with pool.acquire() as con:
        return await con.fetch(query, *args)

async def fetchrow(query, *args):
    async with pool.acquire() as con:
        return await con.fetchrow(query, *args)

async def execute(query, *args):
    async with pool.acquire() as con:
        return await con.execute(query, *args)
