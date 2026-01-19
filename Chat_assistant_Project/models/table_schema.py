from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text,LargeBinary
from database.db import engine

Base = declarative_base()

class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True)
    msg = Column(String, nullable=False)
    reply = Column(Text, nullable=False)
    file_content = Column(Text, nullable=True)

class GeneratedImage(Base):
    __tablename__ = "generated_images"
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(String, index=True)
    prompt = Column(String)
    image_data = Column(LargeBinary)   


Base.metadata.create_all(engine)

