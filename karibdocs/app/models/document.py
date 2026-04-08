

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_documents_user_created_at", "user_id", "created_at"),
    )

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    filename        = Column(String(255), nullable=False)
    original_name   = Column(String(255), nullable=False)
    file_type       = Column(String(50))
    file_size       = Column(Integer)
    source          = Column(String(50), default="upload")   # "upload" ou "drive"
    drive_file_id   = Column(String(255), nullable=True)
    is_indexed      = Column(Boolean, default=False)
    chunk_count     = Column(Integer, default=0)
    collection_name = Column(String(255))
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("Utilisateur")