from typing import List, Annotated, Optional

from fastapi import APIRouter, HTTPException, Depends, Path, Query
import app.models.option as models
from app.core.db import engine, SessionLocal
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/options",
    tags=["options"],
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

option_db: List[models.Option] = []


# @router.get("/", response_model=List[models.Option])
@router.get("/")
def get_options(
    db: Session = Depends(get_db),
    first_n: Annotated[Optional[int], Query(title="Number of options to retrieve", ge=1)] = None,
    offset: Annotated[Optional[int], Query(title="Starting index of range", ge=0)] = 0
):
    # if first_n:
    #     if offset + first_n > len(option_db):
    #         raise HTTPException(status_code=400, detail="Requested range exceeds available options")
    #     return option_db[offset: offset + first_n]
    
    # return option_db
    return db.query(models.Options).all()


@router.get("/{option_id}", response_model=models.Option)
def get_option(
    option_id: Annotated[int, Path(title="The ID of the option to retrieve", ge=0)]
):
    for option in option_db:
        if option.id == option_id:
            return option
    raise HTTPException(status_code=404, detail="Option contract not found")


# @router.post("/create", response_model=models.Option)
@router.post("/create")
def create_option(
    option: models.OptionCreate,
    db: Session = Depends(get_db)
):
    # new_id = len(option_db) + 1
    # new_option = models.Option (
    #     id = new_id,
    #     contract_type = option.contract_type,
    #     exercise_style = option.exercise_style, 
    #     strike_price = option.strike_price,
    #     expiration_date = option.expiration_date
    # )
    # option_db.append(new_option)

    option_model = models.Options()
    option_model.type = option.contract_type
    option_model.style = option.exercise_style
    option_model.strike_price = option.strike_price
    option_model.expiration_date = option.expiration_date

    db.add(option_model)
    db.commit()

    # return new_option


@router.put("/{option_id}", response_model=models.Option)
def update_option(
    option_id: Annotated[int, Path(title="The ID of the option to update", ge=0)], 
    updated_option: models.OptionUpdate
):
    for option in option_db:
        if option.id == option_id:
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


@router.delete("/{option_id}")
def delete_option(
    option_id: Annotated[int, Path(title="The ID of the option to delete", ge=0)]
):
    for index, option in enumerate(option_db):
        if option.id == option_id:
            del option_db[index]
            return {"detail": "Option contract deleted"}
    raise HTTPException(status_code=404, detail="Option contract not found")