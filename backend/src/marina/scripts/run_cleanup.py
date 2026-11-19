import asyncio
import os
import sys

# Ensure backend/src is in python path
sys.path.insert(0, os.path.abspath("backend/src"))

from marina.db.session import AsyncSessionLocal
from marina.services.season_cleanup_service import SeasonCleanupService


async def main():
    async with AsyncSessionLocal() as session:
        service = SeasonCleanupService(session)
        result = await service.isolate_historical_data()
        print("Cleanup completed successfully:")
        for k, v in result.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    asyncio.run(main())
