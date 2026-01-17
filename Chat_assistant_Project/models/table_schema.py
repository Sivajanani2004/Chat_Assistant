from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text
from database.db import engine

Base = declarative_base()

class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True)
    msg = Column(String, nullable=False)
    reply = Column(Text, nullable=False)
    file_content = Column(Text, nullable=True)

Base.metadata.create_all(engine)
