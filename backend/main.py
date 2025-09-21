from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import requests
import os

load_dotenv()  # Load environment variables from .env file
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

if not POLYGON_API_KEY:
    raise RuntimeError("POLYGON_API_KEY environment variable not set.")

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello World"}
