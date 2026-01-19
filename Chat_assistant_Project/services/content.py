import os,uuid
import shutil,requests
from sqlalchemy.orm import Session
from models.schema import chatRequest
from models.table_schema import Chat,GeneratedImage
from services.file import extract_file_text, image_to_base64, is_image
from groq import Groq
from fastapi import HTTPException

client = Groq(api_key="GROQ_API_KEY")

def generate_chat_title(msg: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Generate a short chat title with 3 or 4 words and give the title based on user given message. Do not use quotes."
            },
            {
                "role": "user",
                "content": msg
            }
        ],
        max_completion_tokens=20)
    return response.choices[0].message.content.strip()

def get_reply(msg: str, chat_id: str, file, db: Session):

    history = (db.query(Chat).filter(Chat.chat_id == chat_id).order_by(Chat.id.desc()).limit(5).all()[::-1])

    messages = [{"role": "system", "content": "You are a helpful AI assistant."}]

    last_user_msg = None

    for chat in history:
        messages.append({"role": "user", "content": chat.msg})
        messages.append({"role": "assistant", "content": chat.reply})
        last_user_msg = chat.msg

    file_text = None
    image_base64 = None

    if file:
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        if is_image(file_path):
            image_base64 = image_to_base64(file_path)
        else:
            file_text = extract_file_text(file_path)
            if file_text:
                messages.append({"role": "user", "content": file_text})
                last_user_msg = file_text

    instruction = msg.lower()

    if any(k in instruction for k in ["summarise", "translate", "extract"]):
        if last_user_msg:
            messages.append({"role": "user", "content": f"{msg}\n\n{last_user_msg}"})
        else:
            messages.append({"role": "user", "content": msg})
    else:
        messages.append({"role": "user", "content": msg})

    if image_base64:
        response = client.chat.completions.create(
            model="llama-3.2-vision-preview",
            messages=[{
                "role": "user",
                "content": [{"type": "text", "text": msg or "Describe this image"},
                            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_base64}"}
                    ]}])
        reply = response.choices[0].message.content
    else:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_completion_tokens=8192,
            messages=messages)
        
        reply = response.choices[0].message.content

    existing = db.query(Chat).filter(Chat.chat_id == chat_id).first()

    if existing:
        title = existing.title
    else:
        title = generate_chat_title(msg)


    chat_entry = Chat(
        chat_id=chat_id,
        title=title,
        msg=msg,
        reply=reply,
        file_content=file_text)

    db.add(chat_entry)
    db.commit()

    return reply


def fetch_chat_history(db: Session, chat_id: str):
    chats = (db.query(Chat).filter(Chat.chat_id == chat_id).order_by(Chat.id).all())
    history = []
    for chat in chats:
        history.append({"role": "user", "content": chat.msg})
        history.append({"role": "assistant", "content": chat.reply})

    return history


def get_chat_sessions(db: Session):
    chats = db.query(Chat.chat_id, Chat.title).distinct().all()
    return [{"chat_id": c.chat_id, "title": c.title} for c in chats]


def clear_chat_history(db: Session, chat_id: str | None = None):
    if chat_id:
        db.query(Chat).filter(Chat.chat_id == chat_id).delete()
    else:
        db.query(Chat).delete()
    db.commit()



def generate_image_service(prompt: str, db: Session) -> bytes:
    HF_API_KEY = "HF_API"
    HF_URL = "YOUR_HF_URL"

    headers = {"Authorization": f"Bearer {HF_API_KEY}","Content-Type": "application/json"}
    response = requests.post(HF_URL,headers=headers,json={"inputs": prompt})

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Image generation failed")

    image_bytes = response.content

    image_entry = GeneratedImage(image_id=str(uuid.uuid4()),prompt=prompt,image_data=image_bytes)

    db.add(image_entry)
    db.commit()

    return image_bytes  