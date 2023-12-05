import os
from dotenv import load_dotenv
import asyncpg
from async_lru import alru_cache


load_dotenv()


@alru_cache()
async def connect_to_db():
    return await asyncpg.connect(
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        database=os.getenv("PG_DATABASE"),
        host=os.getenv("PG_HOST"),
        port=int(os.getenv("PG_PORT")),
    )


async def close_db_connection(conn):
    await conn.close()
