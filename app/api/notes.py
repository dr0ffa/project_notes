from fastapi import APIRouter, Depends, Request, Response, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import delete
from uuid import UUID
from app.schemas.notes_schemas import NoteCreateRequest, NoteResponse, NoteRequest, NoteDeleteRequest
from app.models_bd.database import get_db
from app.api.auth import security
from app.models_bd.models import Notes, Tags


notes_router = APIRouter()

@notes_router.post("/notes/create_note")
async def create_note(note: NoteCreateRequest, request: Request, db: Session = Depends(get_db)):
    token = await security.access_token_required(request)
    user_id = token.sub
    new_note = Notes(tag=note.tag, user_id=user_id, note=note.note)
 
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return {"result": "note add"}

@notes_router.get("/notes/get_all_notes")
async def get_all_notes(request: Request, db: Session = Depends(get_db)):
    token = await security.access_token_required(request)
    user_id = token.sub
    notes = db.query(Notes).filter(Notes.user_id == user_id).all()
    return notes

@notes_router.get("/notes/get_note", response_model = NoteResponse)
async def get_note(note_id: UUID = Query(..., description="id"), db: Session = Depends(get_db)):
    note = db.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Not found")
    return NoteResponse.model_validate(note)

@notes_router.post("/notes/delete_note")
async def delete_note(note: NoteDeleteRequest, request: Request, db: Session = Depends(get_db)):
    token = await security.access_token_required(request)
    user_id = token.sub
    try:
        if not db.query(Notes).filter(Notes.user_id == user_id).count():
            raise HTTPException(status_code=404, detail="User has no notes")

        if note.note_id is None and note.tag is None:
            token = await security.access_token_required(request)
            user_id = token.sub
            data = delete(Notes).where(Notes.user_id == user_id)
            db.execute(data)
            db.commit()
            return {"update": "all notes deleted"}
        
        elif note.note_id is None and note.tag is not None:
            if not db.query(Notes).filter(Notes.tag == note.tag).count():
                raise HTTPException(status_code=404, detail=f"No notes with tag '{note.tag}' found")
            
            data = delete(Notes).where(Notes.tag == note.tag)
            db.execute(data)
            db.commit()
            return {"update": f"all notes with tag '{note.tag}' deleted"}
        
        elif note.note_id is not None and note.tag is None:
            if not db.query(Notes).filter(Notes.id == note.note_id).count():
                raise HTTPException(status_code=404, detail="Note not found")
            
            data = delete(Notes).where(Notes.id == note.note_id)
            db.execute(data)
            db.commit()
            return {"update": f"note deleted"}
    except Exception as e:
      raise HTTPException(status_code=401, detail={str(e)})
    
@notes_router.get("/notes/get_note_tag")
async def get_note_tag(note_tag: str = (Query(..., description="tag")),  db: Session = Depends(get_db)):
    
    allowed_tags = [tag.value for tag in Tags]
    if note_tag not in allowed_tags:
        raise HTTPException(status_code=422, detail=f"Invalid tag. Allowed values: {allowed_tags}")
    
    notes = db.query(Notes).filter(Notes.tag == note_tag).all()
    try:
        if not notes:
            raise HTTPException(status_code=404, detail="Not found")
        return [NoteResponse.model_validate(note) for note in notes]
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Not found: {str(e)}")