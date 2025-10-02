from pydantic import BaseModel, Field
from enum import Enum
from datetime import date
from decimal import Decimal
from typing import Annotated

class ContractType(str, Enum):
    CALL = 'call'
    PUT = 'put'

class ExerciseStyle(str, Enum):
    AMERICAN = 'american'
    EUROPEAN = 'european'

class OptionContract(BaseModel):
    contract_type: ContractType
    exercise_style: ExerciseStyle
    strike_price: Annotated[Decimal, Field(gt=0)]
    expiration_date: date