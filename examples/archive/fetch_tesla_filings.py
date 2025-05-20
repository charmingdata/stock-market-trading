import asyncio
from src.edgar_client import EdgarClient

async def main():
    client = EdgarClient()
    filings = await client.get_company_filings(
        cik="1318605",  # Tesla's CIK
        form_type="10-K",
        year=2024
    )
    print(filings)

if __name__ == "__main__":
    asyncio.run(main())

