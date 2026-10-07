import json
import urllib.request
import urllib.error
import os


# ============================================================
# ZAYRA AI CONFIGURATION
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY environment variable is missing."
    )


# ============================================================
# GEMINI API
# ============================================================

API_URL = (
    f"https://generativelanguage.googleapis.com/"
    f"v1beta/models/{MODEL}:generateContent"
)


# ============================================================
# ZAYRA SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are ZAYRA, a helpful AI assistant.

Your answers should be:
- Clear
- Accurate
- Helpful
- Easy to understand
- Concise when the user asks for a short answer

If the user asks for an explanation, explain step by step when useful.

Do not claim to have abilities or access that you do not actually have.
"""


# ============================================================
# CHAT FUNCTION
# ============================================================

def chat_with_zayra(message, history=None):

    if not message or not message.strip():
        return "Please enter a message."

    if history is None:
        history = []

    # Keep only recent conversation
    history = history[-20:]

    contents = []

    # Previous conversation
    for item in history:

        role = item.get("role")
        text = item.get("text", "")

        if not text:
            continue

        if role == "user":
            contents.append({
                "role": "user",
                "parts": [
                    {
                        "text": text
                    }
                ]
            })

        elif role == "assistant":
            contents.append({
                "role": "model",
                "parts": [
                    {
                        "text": text
                    }
                ]
            })

    # Current user message
    contents.append({
        "role": "user",
        "parts": [
            {
                "text": message
            }
        ]
    })

    payload = {
        "systemInstruction": {
            "parts": [
                {
                    "text": SYSTEM_INSTRUCTION
                }
            ]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024
        }
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=data,
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

    try:

        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            response_data = response.read().decode(
                "utf-8"
            )

            result = json.loads(response_data)

        candidates = result.get("candidates", [])

        if not candidates:
            return "ZAYRA could not generate a response."

        content = candidates[0].get(
            "content",
            {}
        )

        parts = content.get(
            "parts",
            []
        )

        if not parts:
            return "ZAYRA returned an empty response."

        text = parts[0].get(
            "text",
            ""
        )

        if not text:
            return "ZAYRA returned an empty response."

        return text.strip()

    except urllib.error.HTTPError as error:

        try:
            error_body = error.read().decode(
                "utf-8"
            )
        except Exception:
            error_body = ""

        return (
            f"Gemini API Error ({error.code}): "
            f"{error_body}"
        )

    except urllib.error.URLError as error:

        return (
            "Network error while connecting "
            f"to Gemini: {error.reason}"
        )

    except Exception as error:

        return (
            "Unexpected ZAYRA error: "
            f"{str(error)}"
        )


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print("ZAYRA AI test started.")
    print("Type 'exit' to stop.\n")

    history = []

    while True:

        try:
            user_message = input("You: ")

        except KeyboardInterrupt:
            print("\nZAYRA stopped.")
            break

        if user_message.lower().strip() == "exit":
            print("ZAYRA stopped.")
            break

        if not user_message.strip():
            continue

        reply = chat_with_zayra(
            user_message,
            history
        )

        print("\nZAYRA:", reply)
        print()

        history.append({
            "role": "user",
            "text": user_message
        })

        history.append({
            "role": "assistant",
            "text": reply
        })
