import asyncio
from parser import ExcelParser


async def main():
    await ExcelParser.process_excel_file()


if __name__ == "__main__":
    asyncio.run(main())
