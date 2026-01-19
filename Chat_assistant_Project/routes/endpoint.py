from fastapi import APIRouter,Depends,UploadFile,File,Form,Response
from sqlalchemy.orm import Session
from database.db import SessionLocal
from models.schema import chatResponse,ImageRequest
from services.content import get_reply,fetch_chat_history,clear_chat_history,get_chat_sessions,generate_image_service


router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/chat", response_model=chatResponse)
def chat(msg: str = Form(...),chat_id: str = Form(...),file: UploadFile | None = File(None),db: Session = Depends(get_db)):
    reply = get_reply(msg, chat_id, file, db)
    return {"msg": msg, "reply": reply}
    
@router.get("/chat-sessions")
def chat_sessions(db: Session = Depends(get_db)):
    return get_chat_sessions(db)

@router.get("/get-chat-history/{chat_id}")
def get_chat_history(chat_id: str, db: Session = Depends(get_db)):
    return fetch_chat_history(db, chat_id)

@router.delete("/delete-chat-history/{chat_id}")
def delete_chat(chat_id: str, db: Session = Depends(get_db)):
    clear_chat_history(db, chat_id)
    return {"message": "Chat deleted"}

@router.delete("/chat-history")
def delete_all_chats(db: Session = Depends(get_db)):
    clear_chat_history(db)
    return {"message": "All chat history cleared"}

@router.post("/generate-image")
def generate_image(data: ImageRequest,db: Session = Depends(get_db)):
    image_bytes = generate_image_service(data.prompt,db)
    return Response(content=image_bytes,media_type="image/png")