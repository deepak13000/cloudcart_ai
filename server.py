from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agents.cloudcart_agent import get_prompt_manager, safe_cloudcart_agent


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


@app.on_event("startup")
async def startup_event() -> None:
    await run_in_threadpool(get_prompt_manager)


@app.get("/api/health")
def health_check():
    return {"ok": True, "service": "CloudCart AI API"}


@app.post("/api/chat")
async def chat(payload: ChatRequest):
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    return await run_in_threadpool(safe_cloudcart_agent, payload.message)
