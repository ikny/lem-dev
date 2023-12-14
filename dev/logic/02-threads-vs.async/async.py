import asyncio
import aioconsole

more = True

async def my_input() -> None:
    global more
    f = await aioconsole.ainput()
    more = False
    print(f)

async def print_numbers() -> None:
    global more
    i = 0
    while more:
        i += 1
        await asyncio.sleep(0)  # sleep for a bit to allow other tasks to run
    print(i)

async def main() -> None:
    await asyncio.gather(my_input(), print_numbers())

if __name__ == "__main__":
    asyncio.run(main())