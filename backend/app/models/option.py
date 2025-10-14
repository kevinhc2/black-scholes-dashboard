import enum
import sqlalchemy
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import Annotated, Optional
from uuid import UUID

from app.core.db import Base

class ContractType(str, enum.Enum):
    CALL = 'call'
    PUT = 'put'


class ExerciseStyle(str, enum.Enum):
    AMERICAN = 'american'
    EUROPEAN = 'european'


class Options(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(sqlalchemy.Enum(ContractType), nullable=False)
    style= Column(sqlalchemy.Enum(ExerciseStyle), nullable=False)
    strike_price = Column(Integer)
    expiration_date = Column(String)


class OptionBase(BaseModel):
    contract_type: Annotated[ContractType, Field(description="Option contract type, either 'call' or 'put'")]
    exercise_style: Annotated[ExerciseStyle, Field(description="either 'american' or 'european'")]
    strike_price: Annotated[int, Field(gt=0)]
    expiration_date: Annotated[date, Field(description="date of maturity in YYYY-MM-DD format")]


class OptionCreate(OptionBase):
    pass


class Option(OptionBase):
    id: UUID


class OptionUpdate(BaseModel):
    contract_type: Annotated[Optional[ContractType], Field(None, description="Option contract type, either 'call' or 'put'")]
    exercise_style: Annotated[Optional[ExerciseStyle], Field(None, description="either 'american' or 'european'")]
    strike_price: Annotated[Optional[int], Field(None, gt=0)]
    expiration_date: Annotated[Optional[date], Field(None, description="date of maturity in YYYY-MM-DD format")]