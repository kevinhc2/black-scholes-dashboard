from typing import List, Annotated, Optional
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, Path, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from models.option import OptionCreate, Option, OptionUpdate
from models.user import User, UserInDB
from models.token import Token, TokenData
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

SECRET_KEY = "233b783628c5f8c310e6fb33247d088ac06822d1fc9a539b6e4f4e6296c4c050"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

users_db = {
    "johndoe" : {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$WiDaxvxYcR+Bf2FGSUY6SQ$mu80jZAD6HYz91GkNvTZmQo+WQyDypHnYLIHV2H10UI",
        "disabled": False,
    },
    "alice" : {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "secret2",
        "disabled": True,
    }
}

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    
def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]

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