from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TrunkBase(BaseModel):
    name: str
    host: str
    prefix: Optional[str] = None
    codecs: Optional[str] = None
    max_channels: Optional[int] = 10
    is_active: Optional[bool] = True

class TrunkCreate(TrunkBase):
    pass

class TrunkUpdate(TrunkBase):
    pass

class TrunkOut(TrunkBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True 