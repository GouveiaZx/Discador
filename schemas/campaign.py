"""
Schemas Pydantic para Campaign
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from database.models import CampaignStatus

class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    cli_number: str = Field(..., min_length=10, max_length=20)
    audio_url: Optional[str] = None
    audio_file_path: Optional[str] = None
    start_time: str = Field(default="09:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    end_time: str = Field(default="18:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    timezone: str = Field(default="America/Argentina/Buenos_Aires")
    max_attempts: int = Field(default=3, ge=1, le=10)
    retry_interval: int = Field(default=30, ge=5, le=1440)  # 5 min a 24h
    max_concurrent_calls: int = Field(default=5, ge=1, le=50)

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    cli_number: Optional[str] = Field(None, min_length=10, max_length=20)
    audio_url: Optional[str] = None
    audio_file_path: Optional[str] = None
    start_time: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    end_time: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    timezone: Optional[str] = None
    max_attempts: Optional[int] = Field(None, ge=1, le=10)
    retry_interval: Optional[int] = Field(None, ge=5, le=1440)
    max_concurrent_calls: Optional[int] = Field(None, ge=1, le=50)

class CampaignResponse(CampaignBase):
    id: int
    status: CampaignStatus
    created_at: datetime
    updated_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    owner_id: Optional[int]
    
    # Estatísticas (calculadas)
    total_contacts: int = 0
    contacted_count: int = 0
    success_count: int = 0
    
    class Config:
        from_attributes = True

class CampaignList(BaseModel):
    campaigns: List[CampaignResponse]
    total: int
    page: int
    page_size: int 