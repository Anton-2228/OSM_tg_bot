import asyncio
import aiogramHandler
import siteHandler

async def main():
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, aiogramHandler.start)

if __name__ == '__main__':
    asyncio.run(main())
