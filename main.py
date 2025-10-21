import asyncio

from src.okmcko_worker.worker import OkMckoWorker


async def main():
    worker = OkMckoWorker()
    await worker.get_mcko_files_list()
    await worker.close()


asyncio.run(main())
