from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
import requests
import os

load_dotenv()  # Load environment variables from .env file
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

if not POLYGON_API_KEY:
    raise RuntimeError("POLYGON_API_KEY environment variable not set.")

app = FastAPI()

fake_user_option_db = {}
fake_option_db = {}

class OptionContract(BaseModel):
    contract_type: str # Either call or put
    exercise_style: str # Either american or european
    strike_price: float
    expiration_date: str # In the format YYYY-MM-DD

def get_options_contract(ticker: str):
    if ticker not in fake_option_db:
        url = f"https://api.polygon.io/v3/reference/options/contracts/{ticker}?apiKey={POLYGON_API_KEY}"
        res = requests.get(url)
        if res.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch data from Polygon API")
        fake_option_db[ticker] = res.json()
        return res.json()
    return fake_option_db[ticker]

@app.get("/option/{ticker}")
def read_option(ticker: str):
    data = get_options_contract(ticker)
    return data

@app.post("/option/create")
def create_option(option: OptionContract):
    id = len(fake_user_option_db) + 1
    option_dict = option.dict()
    fake_user_option_db[id] = option_dict
    return {"id": id, **option_dict}