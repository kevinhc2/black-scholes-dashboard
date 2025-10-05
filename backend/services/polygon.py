from fastapi import HTTPException

from core.config import settings

import httpx

POLYGON_API_KEY = settings.polygon_api_key

if not POLYGON_API_KEY:
    raise RuntimeError("POLYGON_API_KEY environment variable not set.")

BASE_URL = "https://api.polygon.io/v3"

async def get_options_contract(ticker: str):
    url = f"{BASE_URL}/reference/options/contracts/{ticker}?apiKey={POLYGON_API_KEY}"
    params = {"apiKey": POLYGON_API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, params=params)
            res.raise_for_status()
            return res.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch data from Polygon API: {e.response.text}")
    except httpx.RequestError:
        raise HTTPException(status_code=500, detail=f"An error occurred while requesting data from Polygon API: {str(e)}")
