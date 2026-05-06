from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agents.cloudcart_agent import safe_cloudcart_agent


class ChatRequest(BaseModel):
    message: str


app = FastAPI(title="CloudCart AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"ok": True}


@app.post("/api/chat")
def chat(payload: ChatRequest):
    return safe_cloudcart_agent(payload.message)
