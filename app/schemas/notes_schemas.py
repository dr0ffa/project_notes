from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from app.models_bd.models import Tags
from typing import Optional
from datetime import datetime


class NoteCreateRequest(BaseModel):
    tag: Optional[Tags] = Field(default=None)
    note: str
    
class NoteRequest(BaseModel):
    note_id: UUID

class NoteResponse(BaseModel):
    id: UUID
    tag: Optional[Tags] = Field(default=None)
    note: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NoteDeleteRequest(BaseModel):
    note_id: Optional[UUID] = Field(default=None)
    tag: Optional[Tags] = Field(default=None)
