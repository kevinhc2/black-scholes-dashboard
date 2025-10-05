from typing import List, Annotated, Optional
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, Path, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from core.config import settings
from schemas.option import OptionCreate, Option, OptionUpdate
from schemas.user import User, UserInDB
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

users_db = {
    "johndoe" : {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice" : {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    }
}

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

def fake_hash_password(password: str):
    return "fakehashed" + password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def fake_decode_token(token):
    user = get_user(users_db, token)
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

option_db: List[Option] = []

@app.get("/option/{option_id}", response_model=Option, tags=["Options"])
def get_option(
    option_id: Annotated[int, Path(title="The ID of the option to retrieve", ge=0)]
):
    for option in option_db:
        if option.id == option_id:
            return option
    raise HTTPException(status_code=404, detail="Option contract not found")

@app.get("/options", response_model=List[Option], tags=["Options"])
def get_options(
    token: Annotated[str, Depends(oauth2_scheme)],
    first_n: Annotated[Optional[int], Query(title="Number of options to retrieve", ge=1)] = None,
    offset: Annotated[Optional[int], Query(title="Starting index of range", ge=0)] = 0
):
    if first_n:
        if offset + first_n > len(option_db):
            raise HTTPException(status_code=400, detail="Requested range exceeds available options")
        return option_db[offset: offset + first_n]
    
    return option_db

@app.post("/option/create", response_model=Option, tags=["Options"])
def create_option(
    option: OptionCreate
):
    new_id = len(option_db) + 1
    new_option = Option (
        id = new_id,
        contract_type = option.contract_type,
        exercise_style = option.exercise_style, 
        strike_price = option.strike_price,
        expiration_date = option.expiration_date
    )
    option_db.append(new_option)
    return new_option

@app.put("/options/{option_id}", response_model=Option, tags=["Options"])
def update_option(
    option_id: Annotated[int, Path(title="The ID of the option to update", ge=0)], 
    updated_option: OptionUpdate
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

@app.delete("/options/{option_id}", tags=["Options"])
def delete_option(
    option_id: Annotated[int, Path(title="The ID of the option to delete", ge=0)]
):
    for index, option in enumerate(option_db):
        if option.id == option_id:
            del option_db[index]
            return {"detail": "Option contract deleted"}
    raise HTTPException(status_code=404, detail="Option contract not found")