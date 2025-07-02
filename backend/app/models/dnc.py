from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class DNCList(Base):
    __tablename__ = "dnc_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())

    numbers = relationship("DNCNumber", back_populates="dnc_list", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DNCList(id={self.id}, name={self.name})>"

class DNCNumber(Base):
    __tablename__ = "dnc_numbers"

    id = Column(Integer, primary_key=True, index=True)
    dnc_list_id = Column(Integer, ForeignKey("dnc_lists.id", ondelete="CASCADE"), nullable=False)
    phone_number = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=func.now())

    dnc_list = relationship("DNCList", back_populates="numbers")

    def __repr__(self):
        return f"<DNCNumber(id={self.id}, phone_number={self.phone_number})>" 