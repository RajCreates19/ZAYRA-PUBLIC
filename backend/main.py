from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback

from AI import chat_with_zayra


# ============================================================
# ZAYRA FASTAPI BACKEND
# ============================================================

app = FastAPI(
    title="ZAYRA AI",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# RESPONSE MODEL
# ============================================================

class ChatResponse(BaseModel):
    reply: str


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ZAYRA backend"
    }


# ============================================================
# API STATUS
# ============================================================

@app.get("/api")
async def api_status():
    return {
        "service": "ZAYRA AI",
        "status": "online",
        "endpoint": "/api/chat"
    }


# ============================================================
# CHAT API
# ============================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    message = request.message.strip()

    if not message:
        return ChatResponse(
            reply="Please enter a message."
        )

    print("========== ZAYRA REQUEST ==========")
    print("Message:", message)
    print("===================================")

    try:

        reply = chat_with_zayra(message)

        if reply is None:
            reply = ""

        reply = str(reply).strip()

        print("========== ZAYRA RESPONSE ==========")
        print(reply)
        print("====================================")

        if not reply:
            return ChatResponse(
                reply="ZAYRA returned an empty response."
            )

        return ChatResponse(
            reply=reply
        )

    except Exception as error:

        print("========== ZAYRA BACKEND ERROR ==========")
        print("ERROR:", str(error))
        print()
        print("FULL TRACEBACK:")
        traceback.print_exc()
        print("=========================================")

        return ChatResponse(
            reply="ZAYRA ran into a backend error. Please try again."
        )
