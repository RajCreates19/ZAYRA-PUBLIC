# ============================================================
# ZAYRA - AI ENGINE
# ============================================================

import json
import urllib.request
import urllib.error
from pathlib import Path


# ============================================================
# 1. FIXED BACKEND LOCATION
# ============================================================

BACKEND = Path("/storage/emulated/0/ZAYRA/backend")
CONFIG = BACKEND / "config.py"


# ============================================================
# 2. CHECK CONFIG FILE
# ============================================================

if not CONFIG.exists():
    raise FileNotFoundError(
        "config.py was not found at:\n"
        + str(CONFIG)
    )


# ============================================================
# 3. LOAD CONFIG.PY
# ============================================================

config_data = {}

with open(
    CONFIG,
    "r",
    encoding="utf-8"
) as file:

    config_code = file.read()

exec(
    config_code,
    config_data
)


API_KEY = config_data.get("API_KEY")
MODEL = config_data.get(
    "MODEL",
    "gemini-3.5-flash-lite"
)


if not API_KEY:
    raise ValueError(
        "API_KEY is missing in config.py"
    )


# ============================================================
# 4. GEMINI API URL
# ============================================================

API_URL = (
    "https://generativelanguage.googleapis.com/"
    f"v1beta/models/{MODEL}:generateContent"
)


# ============================================================
# 5. ZAYRA BEHAVIOUR
# ============================================================

SYSTEM_INSTRUCTION = """
You are ZAYRA, a helpful general-purpose AI assistant.

Answer the user's questions naturally and clearly.

Important behavior:

- Be concise by default.
- Give more detail when the user asks for it.
- Use simple and understandable language.
- Maintain conversation context.
- Do not unnecessarily repeat the user's question.
- For educational questions, explain clearly and step by step when useful.
- If the user asks for a short answer, keep the answer short.
- If the user asks for examples, provide useful examples.
- Be conversational and helpful.
"""


# ============================================================
# 6. CONVERSATION HISTORY
# ============================================================

conversation_history = []


# ============================================================
# 7. MAIN ZAYRA FUNCTION
# ============================================================

def chat_with_zayra(message):

    global conversation_history

    message = str(message).strip()

    if not message:
        return "Please enter a message."


    # --------------------------------------------------------
    # Add user message
    # --------------------------------------------------------

    conversation_history.append(
        {
            "role": "user",
            "parts": [
                {
                    "text": message
                }
            ]
        }
    )


    # --------------------------------------------------------
    # Limit history
    # --------------------------------------------------------

    if len(conversation_history) > 20:

        conversation_history = (
            conversation_history[-20:]
        )


    # --------------------------------------------------------
    # Prepare Gemini request
    # --------------------------------------------------------

    request_data = {

        "system_instruction": {
            "parts": [
                {
                    "text": SYSTEM_INSTRUCTION
                }
            ]
        },

        "contents": conversation_history
    }


    request_body = json.dumps(
        request_data
    ).encode("utf-8")


    # ========================================================
    # 8. CREATE REQUEST
    # ========================================================

    request = urllib.request.Request(
        API_URL,
        data=request_body,
        method="POST"
    )


    request.add_header(
        "Content-Type",
        "application/json"
    )

    request.add_header(
        "x-goog-api-key",
        API_KEY
    )


    # ========================================================
    # 9. SEND REQUEST
    # ========================================================

    try:

        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            response_text = (
                response
                .read()
                .decode("utf-8")
            )


        result = json.loads(
            response_text
        )


        # ----------------------------------------------------
        # Check candidates
        # ----------------------------------------------------

        candidates = result.get(
            "candidates",
            []
        )


        if not candidates:

            return (
                "ZAYRA could not generate a response."
            )


        # ----------------------------------------------------
        # Extract response
        # ----------------------------------------------------

        content = candidates[0].get(
            "content",
            {}
        )

        parts = content.get(
            "parts",
            []
        )


        answer_parts = []


        for part in parts:

            text = part.get("text")

            if text:

                answer_parts.append(
                    text
                )


        answer = "\n".join(
            answer_parts
        ).strip()


        if not answer:

            return (
                "ZAYRA returned an empty response."
            )


        # ----------------------------------------------------
        # Save model response
        # ----------------------------------------------------

        conversation_history.append(
            {
                "role": "model",
                "parts": [
                    {
                        "text": answer
                    }
                ]
            }
        )


        return answer


    # ========================================================
    # 10. GEMINI HTTP ERROR
    # ========================================================

    except urllib.error.HTTPError as error:

        try:

            error_text = (
                error
                .read()
                .decode("utf-8")
            )

        except Exception:

            error_text = (
                "No additional error information."
            )


        return (
            f"Gemini API Error ({error.code})\n\n"
            f"{error_text}"
        )


    # ========================================================
    # 11. NETWORK ERROR
    # ========================================================

    except urllib.error.URLError as error:

        return (
            "ZAYRA could not connect to Gemini.\n\n"
            f"{error}"
        )


    # ========================================================
    # 12. OTHER ERROR
    # ========================================================

    except Exception as error:

        return (
            "ZAYRA encountered an unexpected error.\n\n"
            f"{type(error).__name__}: {error}"
        )


# ============================================================
# 13. DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 55)
    print("             ZAYRA AI ENGINE")
    print("=" * 55)

    print()
    print("Config       : FOUND")
    print("API Key      : FOUND")
    print("Model        :", MODEL)
    print("AI Status    : READY")

    print()
    print("-" * 55)

    while True:

        question = input(
            "You: "
        ).strip()


        if question.lower() in {
            "exit",
            "quit",
            "bye"
        }:

            print()
            print("ZAYRA: Goodbye!")
            break


        if not question:
            continue


        print()
        print("ZAYRA:")

        answer = chat_with_zayra(
            question
        )

        print(answer)
        print()
