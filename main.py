import asyncio

from settings import initialize_db, close_db
from src.okmcko_worker.worker import OkMckoWorker


async def main():
    initialize_db()
    worker = OkMckoWorker()
    try:
        while True:
            await worker.send_new_files()
            await asyncio.sleep(1)
    except:
        await worker.close()
        close_db()


asyncio.run(main())
