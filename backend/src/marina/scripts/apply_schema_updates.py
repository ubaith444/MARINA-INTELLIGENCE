"""Apply schema updates to SQLite database."""
import asyncio
from marina.db.session import engine
from marina.db.base import Base
# Import all models to register them on Base.metadata
import marina.models  # noqa: F401


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Schema updates successfully applied.")


if __name__ == "__main__":
    asyncio.run(main())
