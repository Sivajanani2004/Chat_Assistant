from fastapi import FastAPI
from routes.endpoint import router as route

app = FastAPI(title = "Chat-Assistant")

app.include_router(route)