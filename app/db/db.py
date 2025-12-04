import os
import asyncpg
import asyncio

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", verbose=True)

RAILWAY_DATABASE_URL = str(os.getenv("RAILWAY_DATABASE_URL"))

async def main():
    conn = await asyncpg.connect(RAILWAY_DATABASE_URL)

    rows = await conn.fetch("""
        SELECT * FROM public.users;
    """)

    for row in rows:
        print(row['first_name'])
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())