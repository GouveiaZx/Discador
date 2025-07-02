from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.database import Base

class Trunk(Base):
    __tablename__ = "trunks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    host = Column(String(255), nullable=False)
    prefix = Column(String(20), nullable=True)
    codecs = Column(String(100), nullable=True)
    max_channels = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Trunk(id={self.id}, name={self.name}, host={self.host})>" 