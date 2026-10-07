============================================================
                         ZAYRA
              General-Purpose AI Assistant
============================================================

ZAYRA is a general-purpose AI assistant powered by Google
Gemini API.

------------------------------------------------------------
PROJECT STRUCTURE
------------------------------------------------------------

ZAYRA/
|
|-- frontend/
|   |-- index.html
|   |-- style.css
|   |-- app.js
|
|-- backend/
|   |-- server.py
|   |-- AI.py
|   |-- config.py
|
|-- README.txt


------------------------------------------------------------
FRONTEND
------------------------------------------------------------

index.html
Main structure and interface of the ZAYRA web application.

style.css
Controls the complete visual design, themes and responsive
layout for mobile, computer and smartboard screens.

app.js
Controls chat interaction, sidebar, settings, voice input,
voice output, feedback buttons and recent chats.


------------------------------------------------------------
BACKEND
------------------------------------------------------------

server.py
Runs the local web server and connects the frontend with the
ZAYRA AI engine.

AI.py
Handles conversation with the Google Gemini API and maintains
conversation context.

config.py
Stores the Gemini API key and selected Gemini model.


------------------------------------------------------------
AI MODEL
------------------------------------------------------------

Model:
gemini-3.5-flash-lite

The Gemini API is accessed through HTTPS using Python's
standard library.

No external Python packages are required for the current
backend implementation.


------------------------------------------------------------
MAIN FEATURES
------------------------------------------------------------

- General-purpose AI conversation
- Gemini-powered responses
- Responsive web interface
- Hidden sidebar
- New Chat
- Projects
- Settings
- Recent Chats
- Dark theme
- Light theme
- Midnight Blue theme
- Voice input
- Female voice output
- Optional Voice Response
- Voice tone selection
- Like feedback
- Dislike feedback
- Speaker button for ZAYRA responses


------------------------------------------------------------
VOICE BEHAVIOR
------------------------------------------------------------

Voice Response can be enabled or disabled from Settings.

When Voice Response is enabled:

- ZAYRA responses can be spoken automatically.
- A speaker button appears below ZAYRA responses.
- The speaker button can replay the specific response.

Voice input uses browser speech recognition when supported.

Voice output uses the browser's speech synthesis system.

The exact available voice depends on the device and browser.


------------------------------------------------------------
RUNNING ZAYRA
------------------------------------------------------------

1. Open Pydroid 3.

2. Open:

   /storage/emulated/0/ZAYRA/backend/server.py

3. Run server.py.

4. Keep the server running.

5. Open a browser.

6. Visit:

   http://127.0.0.1:8000


------------------------------------------------------------
IMPORTANT
------------------------------------------------------------

Do not run frontend/app.js directly in Pydroid.

app.js is JavaScript and is loaded automatically by the
browser through server.py.

Keep the Gemini API key private.

Do not publish config.py with the API key exposed.


------------------------------------------------------------
PROJECT STATUS
------------------------------------------------------------

Frontend:
READY

AI Engine:
READY

Backend Server:
READY

API:
READY

Final integration:
TESTING


============================================================
                         ZAYRA
============================================================