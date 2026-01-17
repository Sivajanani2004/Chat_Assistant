from fastapi import FastAPI
from routes.endpoint import router as route

api = FastAPI(title = "Chat-Assistant")

api.include_router(route)