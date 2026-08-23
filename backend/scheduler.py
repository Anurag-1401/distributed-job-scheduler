"""Legacy compatibility wrapper. The recommended entry point is `python run.py`."""
import asyncio
from app.scheduler import main

if __name__ == "__main__":
    asyncio.run(main())
