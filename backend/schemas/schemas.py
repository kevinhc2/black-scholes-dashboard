from pydantic import BaseModel, Field
from enum import Enum
from datetime import date
from decimal import Decimal
from typing import Annotated, Optional

class ContractType(str, Enum):
    CALL = 'call'
    PUT = 'put'

class ExerciseStyle(str, Enum):
    AMERICAN = 'american'
    EUROPEAN = 'european'

class OptionBase(BaseModel):
    contract_type: Annotated[ContractType, Field(description="Option contract type, either 'call' or 'put'")]
    exercise_style: Annotated[ExerciseStyle, Field(description="either 'american' or 'european'")]
    strike_price: Annotated[Decimal, Field(gt=0)]
    expiration_date: Annotated[date, Field(description="date of maturity in YYYY-MM-DD format")]

class OptionCreate(OptionBase):
    pass

class Option(OptionBase):
    option_id: int

class OptionUpdate(BaseModel):
    contract_type: Annotated[Optional[ContractType], Field(None, description="Option contract type, either 'call' or 'put'")]
    exercise_style: Annotated[Optional[ExerciseStyle], Field(None, description="either 'american' or 'european'")]
    strike_price: Annotated[Optional[Decimal], Field(None, gt=0)]
    expiration_date: Annotated[Optional[date], Field(None, description="date of maturity in YYYY-MM-DD format")]
