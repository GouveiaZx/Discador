from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AudioBase(BaseModel):
    campaign_id: Optional[int] = None
    type: str
    file_url: str
    description: Optional[str] = None

class AudioCreate(AudioBase):
    pass

class AudioUpdate(AudioBase):
    pass

class AudioOut(AudioBase):
    id: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True 
