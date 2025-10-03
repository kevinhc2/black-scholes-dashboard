from typing import List
from fastapi import FastAPI, HTTPException
from services.polygon_client import get_options_contract
from schemas.schemas import OptionCreate, Option, OptionUpdate

app = FastAPI()

option_db: List[Option] = []

@app.get("/option/{id}", response_model=Option)
def get_option(id: int):
    for option in option_db:
        if option.option_id == id:
            return option
    raise HTTPException(status_code=404, detail="Option contract not found")

@app.get("/options", response_model=List[Option])
def get_options(first_n: int = None, offset: int = 0):
    if first_n:
        return option_db[offset: offset + first_n]
    return option_db

@app.post("/option/create", response_model=Option)
def create_option(option: OptionCreate):
    new_id = len(option_db) + 1
    new_option = Option (
        option_id = new_id,
        contract_type = option.contract_type,
        exercise_style = option.exercise_style, 
        strike_price = option.strike_price,
    )
    option_db.append(new_option)
    return new_option

@app.put("/options/{option_id}", respose_model=Option)
def update_option(option_id: int, updated_option: OptionUpdate):
    for option in option_db:
        if option.option_id == option_id:
            if updated_option.contract_type is not None:
                option.contract_type = updated_option.contract_type
            if updated_option.exercise_style is not None:
                option.exercise_style = updated_option.exercise_style
            if updated_option.strike_price is not None:
                option.strike_price = updated_option.strike_price
            if updated_option.expiration_date is not None:
                option.expiration_date = updated_option.expiration_date
            return option
    
    raise HTTPException(status_code=404, detail="Option contract not found")

@app.delete("/options/{option_id}")
def delete_option(option_id: int):
    for index, option in enumerate(option_db):
        if option.option_id == option_id:
            del option_db[index]
            return {"detail": "Option contract deleted"}
    raise HTTPException(status_code=404, detail="Option contract not found")