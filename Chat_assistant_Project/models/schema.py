from pydantic import BaseModel

class chatRequest(BaseModel):
    msg: str

class chatResponse(BaseModel):
    msg: str
    reply: str

class ImageRequest(BaseModel):
    prompt: str