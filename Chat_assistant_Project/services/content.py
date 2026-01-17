import os
import shutil
from sqlalchemy.orm import Session
from models.schema import chatRequest
from models.table_schema import Chat
from services.file import extract_file_text, image_to_base64, is_image
from groq import Groq

client = Groq(api_key="GROQ_API_KEY")

def get_reply(msg:str, file, db: Session):
    history = db.query(Chat).order_by(Chat.id.desc()).limit(5).all()[::-1]

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

    if any(k in instruction for k in ["summarise","translate","extract"]):
        if last_user_msg:
            messages.append({"role": "user","content": f"{msg}\n\n{last_user_msg}"})
        else:
            messages.append({"role": "user", "content":msg})
    else:
        messages.append({"role": "user", "content": msg})

    if image_base64:
        response = client.chat.completions.create(
            model="llama-3.2-vision-preview",
            messages=[{"role": "user",
                "content": [
                    {"type": "text", "text": msg or "Describe this image"},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_base64}"}]
            }])
        reply = response.choices[0].message.content
    else:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_completion_tokens=8192,
            messages=messages)
        reply = response.choices[0].message.content

    chat_entry = Chat(
        msg= msg,
        reply=reply,
        file_content=file_text)
    db.add(chat_entry)
    db.commit()

    return reply
