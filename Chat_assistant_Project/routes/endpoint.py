from fastapi import APIRouter,Depends,UploadFile,File,Form
from sqlalchemy.orm import Session
from database.db import SessionLocal
from models.schema import chatRequest,chatResponse
from services.content import get_reply


router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/chat", response_model=chatResponse)
def chat(msg: str = Form(...),file: UploadFile | None = File(None),db: Session = Depends(get_db)):
    reply = get_reply(msg, file, db)
    return {"msg":msg,"reply": reply}
    
