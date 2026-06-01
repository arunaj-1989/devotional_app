from fastapi import FastAPI, Request, Form, HTTPException
from a2wsgi import ASGIMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
import json
import os

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SECRET_KEY", "fallback-secret-key"))

# Define the base directory for static files and templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
VERSES_FILE_PATH = os.path.join(BASE_DIR, "verses.txt")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Registry of available stotrams. Add new ones here!
STOTRAMS_CONFIG = {
    "lalitha": {
        "title": "Lalitha Sahasranama",
        "description": "1000 names of the Divine Mother Tripurasundari.",
        "icon": "🌺",
        "files": {
            "verses": "verses.txt",
            "landing_mal": "landing-page-malayalam.txt",
            "landing_san": "landing-page-sanskrit.txt",
            "end_mal": "end-page-malayalam.txt",
            "end_san": "end-page-sanskrit.txt"
        }
    },
        "Vishnu": {
        "title": "Vishnu Sahasranama",
        "description": "1000 names of Lord Vishnu.",
        "icon": "🌺",
        "files": {
            "verses": "vishnu_verses.txt",
            "landing_mal": "vishnu_landing-page-malayalam.txt",
            "landing_san": "vishnu_landing-page-sanskrit.txt",
            "end_mal": "vishnu_end-page-malayalam.txt",
            "end_san": "vishnu_end-page-sanskrit.txt"
        }
    }
}

# Global storage for loaded data: { "stotram_id": { "verses": [], ... } }
STOTRAMS_DATA = {}

def load_verses():
    global STOTRAMS_DATA
    for sid, config in STOTRAMS_CONFIG.items():
        data = {"verses": [], "landing_mal": "", "landing_san": "", "end_mal": "", "end_san": ""}
        files = config["files"]
        
        try:
            v_path = os.path.join(BASE_DIR, files["verses"])
            if os.path.exists(v_path):
                with open(v_path, "r", encoding="utf-8") as f:
                    data["verses"] = json.load(f)
            
            def read_txt(key):
                path = os.path.join(BASE_DIR, files[key])
                return open(path, "r", encoding="utf-8").read().strip() if os.path.exists(path) else ""

            data["landing_mal"] = read_txt("landing_mal")
            data["landing_san"] = read_txt("landing_san")
            data["end_mal"] = read_txt("end_mal")
            data["end_san"] = read_txt("end_san")
            STOTRAMS_DATA[sid] = data
        except Exception as e:
            print(f"Error loading {sid}: {e}")

# Load verses when the app starts
@app.on_event("startup")
async def startup_event():
    load_verses()

@app.get("/")
async def home_page(request: Request):
    stotrams = [
        {"id": k, "title": v["title"], "description": v["description"], "icon": v["icon"]}
        for k, v in STOTRAMS_CONFIG.items()
    ]
    return templates.TemplateResponse(
        request=request, 
        name="home.html", 
        context={"stotrams": stotrams}
    )

@app.get("/stotram/{stotram_id}/flashcard/{verse_id}")
async def get_flashcard(request: Request, stotram_id: str, verse_id: int):
    # Get language from query parameter or session, default to 'sanskrit'
    lang = request.query_params.get("lang", request.session.get("language", "sanskrit"))
    # Ensure 'lang' is always a string before storing in session
    if not isinstance(lang, str):
        lang = "sanskrit" # Fallback to default if it somehow became a non-string

    stotram = STOTRAMS_DATA.get(stotram_id)
    if not stotram:
        raise HTTPException(status_code=404, detail="Stotram not found")

    verses = stotram["verses"]
    count = len(verses)

    # Boundary check: 0 is Landing, count + 1 is End
    if not (0 <= verse_id <= count + 1):
        raise HTTPException(status_code=404, detail=f"Page {verse_id} not found.")

    # Store language in session for subsequent requests
    request.session["language"] = lang
    
    if verse_id == 0:
        verse = {"sanskrit": stotram["landing_san"], "malayalam": stotram["landing_mal"], 
                 "english": "Dhyanam", "meaning": "Opening Prayers"}
    elif verse_id == count + 1:
        verse = {"sanskrit": stotram["end_san"], "malayalam": stotram["end_mal"], 
                 "english": "Conclusion", "meaning": "Closing Prayers"}
    else:
        verse = verses[verse_id - 1]

    return templates.TemplateResponse(
        request=request,
        name="flashcard.html",
        context={
            "verse": verse,
            "current_id": verse_id,
            "total_verses": count + 1,
            "selected_language": lang,
            "languages": ["sanskrit", "malayalam"],
            "stotram_id": stotram_id,
            "stotram_title": STOTRAMS_CONFIG[stotram_id]["title"]
        }
    )
    
@app.post("/stotram/{stotram_id}/flashcard/{verse_id}")
async def post_flashcard(request: Request, stotram_id: str, verse_id: int, direction: str = Form(None), selected_language: str = Form(None)):
    if stotram_id not in STOTRAMS_DATA:
        raise HTTPException(status_code=404, detail="Stotram not found")
    
    total_count = len(STOTRAMS_DATA[stotram_id]["verses"])
    current_id = verse_id
    new_lang = request.session.get("language", "sanskrit")
    if not isinstance(new_lang, str):
        new_lang = "sanskrit" # Fallback to default

    if selected_language:
        new_lang = selected_language
        # Ensure selected_language is a string before storing in session
        if not isinstance(new_lang, str):
            new_lang = "sanskrit" # Fallback to default
        request.session["language"] = new_lang
    
    new_id = current_id
    if direction == "next":
        new_id = min(current_id + 1, total_count + 1)
    elif direction == "prev":
        new_id = max(current_id - 1, 0)
    
    # Redirect to the GET endpoint with the new ID and selected language
    return RedirectResponse(url=f"/stotram/{stotram_id}/flashcard/{new_id}?lang={new_lang}", status_code=303)

# WSGI bridge for PythonAnywhere
application = ASGIMiddleware(app)