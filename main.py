from flask import Flask, render_template, request, redirect, url_for, session, abort
import json
import os

# Define the base directory for static files and templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Global storage for loaded data
STOTRAMS_DATA = {}

# Registry of available stotrams
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

# Load stotram data at startup
load_verses()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret-key")

@app.route("/")
def home_page():
    stotrams = [
        {"id": k, "title": v["title"], "description": v["description"], "icon": v["icon"]}
        for k, v in STOTRAMS_CONFIG.items()
    ]
    return render_template("home.html", stotrams=stotrams)

@app.route("/stotram/<stotram_id>/flashcard/<int:verse_id>")
def get_flashcard(stotram_id, verse_id):
    # Get language from query param or session
    lang = request.args.get("lang") or session.get("language", "sanskrit")
    stotram = STOTRAMS_DATA.get(stotram_id)
    if not stotram:
        abort(404, description="Stotram not found")

    verses = stotram["verses"]
    count = len(verses)

    if not (0 <= verse_id <= count + 1):
        abort(404, description=f"Page {verse_id} not found.")

    session["language"] = lang
    
    if verse_id == 0:
        verse = {"sanskrit": stotram["landing_san"], "malayalam": stotram["landing_mal"], 
                 "english": "Dhyanam", "meaning": "Opening Prayers"}
    elif verse_id == count + 1:
        verse = {"sanskrit": stotram["end_san"], "malayalam": stotram["end_mal"], 
                 "english": "Conclusion", "meaning": "Closing Prayers"}
    else:
        verse = verses[verse_id - 1]

    if request.headers.get('Accept') == 'application/json':
        return {
            "verse": verse,
            "current_id": verse_id,
            "total_verses": count + 1,
            "selected_language": lang,
            "stotram_title": STOTRAMS_CONFIG[stotram_id]["title"]
        }

    return render_template(
        "flashcard.html",
        verse=verse,
        current_id=verse_id,
        total_verses=count + 1,
        selected_language=lang,
        languages=["sanskrit", "malayalam"],
        stotram_id=stotram_id,
        stotram_title=STOTRAMS_CONFIG[stotram_id]["title"]
    )
    
@app.route("/stotram/<stotram_id>/flashcard/<int:verse_id>", methods=["POST"])
def post_flashcard(stotram_id, verse_id):
    if stotram_id not in STOTRAMS_DATA:
        abort(404, description="Stotram not found")
    
    total_count = len(STOTRAMS_DATA[stotram_id]["verses"])
    new_lang = request.form.get("selected_language") or session.get("language", "sanskrit")
    session["language"] = new_lang
    
    new_id = verse_id
    direction = request.form.get("direction")
    if direction == "next":
        new_id = min(verse_id + 1, total_count + 1)
    elif direction == "prev":
        new_id = max(verse_id - 1, 0)
    
    return redirect(url_for('get_flashcard', stotram_id=stotram_id, verse_id=new_id, lang=new_lang))

if __name__ == "__main__":
    app.run(debug=True)