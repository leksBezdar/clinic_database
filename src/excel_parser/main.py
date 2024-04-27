import os
import asyncio
from .parser import ExcelParser


async def main():
    os.environ["SECURE_COOKIE"] = "False"
    await ExcelParser.process_excel_file()


if __name__ == "__main__":
    asyncio.run(main())
