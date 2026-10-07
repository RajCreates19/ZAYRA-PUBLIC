# ============================================================
# ZAYRA - VERCEL BACKEND ENTRYPOINT
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys


# ============================================================
# PROJECT PATHS
# ============================================================

BACKEND = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND.parent
FRONTEND = PROJECT_ROOT / "frontend"
ASSETS = FRONTEND / "assets"


# ============================================================
# LOAD AI ENGINE
# ============================================================

sys.path.insert(0, str(BACKEND))

from AI import chat_with_zayra


# ============================================================
# CREATE FASTAPI APP
# ============================================================

app = FastAPI(
    title="ZAYRA AI",
    description="ZAYRA AI Backend",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


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
# MAIN CHAT API
# ============================================================

@app.post("/api/chat")
async def chat(request: dict):

    # --------------------------------------------------------
    # Get message
    # --------------------------------------------------------

    message = request.get("message", "")


    # --------------------------------------------------------
    # Validate message
    # --------------------------------------------------------

    if not isinstance(message, str):
        message = str(message)


    message = message.strip()


    if not message:
        return {
            "reply": "Please enter a message."
        }


    # --------------------------------------------------------
    # Send message to ZAYRA AI engine
    # --------------------------------------------------------

    try:

        reply = chat_with_zayra(message)


        # ----------------------------------------------------
        # Make sure reply is valid
        # ----------------------------------------------------

        if reply is None:
            reply = ""


        reply = str(reply).strip()


        if not reply:

            return {
                "reply": "ZAYRA could not generate a response."
            }


        # ----------------------------------------------------
        # Send reply
        # ----------------------------------------------------

        return {
            "reply": reply
        }


    except Exception as error:

        print(
            "[ZAYRA ERROR]",
            str(error)
        )


        return {
            "reply":
            "ZAYRA ran into a problem while answering. Please try again."
        }


# ============================================================
# ROOT TEST ENDPOINT
# ============================================================

@app.get("/api")
async def api_status():

    return {
        "service": "ZAYRA AI",
        "status": "online",
        "endpoint": "/api/chat"
    }


# ============================================================
# STARTUP MESSAGE
# ============================================================

@app.on_event("startup")
async def startup():

    print()
    print("=" * 55)
    print("              ZAYRA VERCEL BACKEND")
    print("=" * 55)
    print()
    print("Backend  : READY")
    print("AI Engine: READY")
    print("API      : READY")
    print()
    print("Endpoint : /api/chat")
    print()
    print("=" * 55)
    print()
