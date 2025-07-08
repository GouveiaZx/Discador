from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DNCNumberBase(BaseModel):
    phone_number: str

class DNCNumberCreate(DNCNumberBase):
    pass

class DNCNumberOut(DNCNumberBase):
    id: int
    dnc_list_id: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

class DNCListBase(BaseModel):
    name: str
    description: Optional[str] = None

class DNCListCreate(DNCListBase):
    pass

class DNCListOut(DNCListBase):
    id: int
    created_at: Optional[datetime]
    numbers: List[DNCNumberOut] = []

    class Config:
        from_attributes = True 
