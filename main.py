import asyncio
from DSbot import run_discord, check_discord_user
from TGbot  import start_telegram, queue


async def main():
    await asyncio.gather(run_discord(), start_telegram())

if __name__ == "__main__":
    asyncio.run(main())
