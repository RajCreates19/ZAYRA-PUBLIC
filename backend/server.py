# ============================================================
# ZAYRA - FINAL WEB SERVER
# ============================================================

from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import sys
import json
import os


# ============================================================
# PROJECT PATHS
# ============================================================

BACKEND = Path(__file__).resolve().parent

PROJECT_ROOT = BACKEND.parent

FRONTEND = PROJECT_ROOT / "frontend"


# ============================================================
# LOAD AI ENGINE
# ============================================================

sys.path.insert(
    0,
    str(BACKEND)
)

from AI import chat_with_zayra


# ============================================================
# FRONTEND FILES
# ============================================================

INDEX_FILE = FRONTEND / "index.html"
CSS_FILE = FRONTEND / "style.css"
JS_FILE = FRONTEND / "app.js"


# ============================================================
# CHECK PROJECT
# ============================================================

if not BACKEND.exists():
    raise FileNotFoundError(
        "Backend folder not found."
    )


if not FRONTEND.exists():
    raise FileNotFoundError(
        "Frontend folder not found."
    )


if not INDEX_FILE.exists():
    raise FileNotFoundError(
        "index.html not found."
    )


if not CSS_FILE.exists():
    raise FileNotFoundError(
        "style.css not found."
    )


if not JS_FILE.exists():
    raise FileNotFoundError(
        "app.js not found."
    )


# ============================================================
# SERVER HANDLER
# ============================================================

class ZAYRAServer(BaseHTTPRequestHandler):

    # --------------------------------------------------------
    # CORS HEADERS
    # --------------------------------------------------------

    def send_cors_headers(self):

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )


    # --------------------------------------------------------
    # SEND FILE
    # --------------------------------------------------------

    def send_file(
        self,
        file_path,
        content_type
    ):

        try:

            with open(
                file_path,
                "rb"
            ) as file:

                data = file.read()


            self.send_response(200)

            self.send_header(
                "Content-Type",
                content_type
            )

            self.send_header(
                "Content-Length",
                str(len(data))
            )

            self.send_header(
                "Cache-Control",
                "no-cache"
            )

            self.send_cors_headers()

            self.end_headers()

            self.wfile.write(data)


        except Exception as error:

            self.send_error(
                500,
                "Could not load file: "
                + str(error)
            )


    # --------------------------------------------------------
    # SEND JSON
    # --------------------------------------------------------

    def send_json(
        self,
        data,
        status=200
    ):

        response = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")


        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(response))
        )

        self.send_header(
            "Cache-Control",
            "no-cache"
        )

        self.send_cors_headers()

        self.end_headers()

        self.wfile.write(response)


    # --------------------------------------------------------
    # OPTIONS REQUEST
    # --------------------------------------------------------

    def do_OPTIONS(self):

        self.send_response(204)

        self.send_cors_headers()

        self.end_headers()


    # ========================================================
    # GET REQUESTS
    # ========================================================

    def do_GET(self):

        # ----------------------------------------------------
        # Main page
        # ----------------------------------------------------

        if self.path == "/":

            self.send_file(
                INDEX_FILE,
                "text/html; charset=utf-8"
            )

            return


        # ----------------------------------------------------
        # CSS
        # ----------------------------------------------------

        if self.path == "/style.css":

            self.send_file(
                CSS_FILE,
                "text/css; charset=utf-8"
            )

            return


        # ----------------------------------------------------
        # JavaScript
        # ----------------------------------------------------

        if self.path == "/app.js":

            self.send_file(
                JS_FILE,
                "application/javascript; charset=utf-8"
            )

            return


        # ----------------------------------------------------
        # Favicon
        # ----------------------------------------------------

        if self.path == "/favicon.ico":

            self.send_response(204)

            self.end_headers()

            return


        # ----------------------------------------------------
        # Unknown page
        # ----------------------------------------------------

        self.send_error(
            404,
            "Page not found"
        )


    # ========================================================
    # POST REQUESTS
    # ========================================================

    def do_POST(self):

        # ----------------------------------------------------
        # Only ZAYRA chat API
        # ----------------------------------------------------

        if self.path != "/api/chat":

            self.send_json(
                {
                    "reply":
                    "API endpoint not found."
                },
                404
            )

            return


        try:

            # ------------------------------------------------
            # Get request size
            # ------------------------------------------------

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )


            # ------------------------------------------------
            # Read body
            # ------------------------------------------------

            body = self.rfile.read(
                content_length
            )


            # ------------------------------------------------
            # Convert JSON
            # ------------------------------------------------

            data = json.loads(
                body.decode("utf-8")
            )


            # ------------------------------------------------
            # Get message
            # ------------------------------------------------

            message = data.get(
                "message",
                ""
            )


            if not isinstance(
                message,
                str
            ):

                message = str(message)


            message = message.strip()


            # ------------------------------------------------
            # Empty message
            # ------------------------------------------------

            if not message:

                self.send_json(
                    {
                        "reply":
                        "Please enter a message."
                    },
                    400
                )

                return


            # ------------------------------------------------
            # Send to ZAYRA AI
            # ------------------------------------------------

            reply = chat_with_zayra(
                message
            )


            # ------------------------------------------------
            # Send response
            # ------------------------------------------------

            self.send_json(
                {
                    "reply": reply
                },
                200
            )


        except json.JSONDecodeError:

            self.send_json(
                {
                    "reply":
                    "Invalid request data."
                },
                400
            )


        except Exception as error:

            self.send_json(
                {
                    "reply":
                    "Server error: "
                    + str(error)
                },
                500
            )


    # ========================================================
    # LOGGING
    # ========================================================

    def log_message(
        self,
        format,
        *args
    ):

        print(
            "[SERVER]",
            format % args
        )


# ============================================================
# START SERVER
# ============================================================

PORT = int(
    os.getenv(
        "PORT",
        "8000"
    )
)


class ZAYRAHTTPServer(
    HTTPServer
):

    allow_reuse_address = True


server = ZAYRAHTTPServer(
    (
        "0.0.0.0",
        PORT
    ),
    ZAYRAServer
)


print()
print("=" * 55)
print("              ZAYRA WEB SERVER")
print("=" * 55)
print()
print("Backend  : READY")
print("AI Engine: READY")
print("Frontend : READY")
print("API      : READY")
print()
print("Port     :", PORT)
print()
print("=" * 55)
print()


try:

    server.serve_forever()


except KeyboardInterrupt:

    print()
    print("ZAYRA server stopped.")


finally:

    server.server_close()
