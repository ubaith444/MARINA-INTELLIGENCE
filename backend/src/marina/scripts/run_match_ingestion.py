"""Script to run match data ingestion service."""
import asyncio
import json
from marina.db.session import AsyncSessionLocal
from marina.services.match_ingestion_service import MatchIngestionService


async def main():
    async with AsyncSessionLocal() as session:
        service = MatchIngestionService(session)
        result = await service.ingest_completed_matches()
        print("Ingestion result:")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
