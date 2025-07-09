import enum
import uuid
from app.models_bd.database import Base, engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

class Tags(str, enum.Enum):
    work = "work"
    study = "study"
    life = "life"
    home = "home"

class Users(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    notes = relationship("Notes", back_populates="user")

class Notes(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tag: Mapped[Tags] = mapped_column(Enum(Tags), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user = relationship("Users", back_populates="notes")

Base.metadata.create_all(bind=engine)
#Base.metadata.drop_all(bind=engine)