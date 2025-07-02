from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from app.database import Base

class Audio(Base):
    __tablename__ = "audios"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campanas.id", ondelete="CASCADE"), nullable=True)
    type = Column(String(50), nullable=False)  # ex: 'main', 'press_2', etc.
    file_url = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Audio(id={self.id}, type={self.type}, campaign_id={self.campaign_id})>" 