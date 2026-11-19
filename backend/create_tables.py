import asyncio
import sys
sys.path.insert(0, "backend/src")

from marina.db.session import engine
from marina.db.base import Base
from marina.models import MatchLineup, MatchSubstitute

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables verified / created successfully.")

if __name__ == "__main__":
    asyncio.run(main())
