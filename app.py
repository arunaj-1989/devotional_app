import json
from pathlib import Path
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & STOTRA DICTIONARY
# ==========================================
st.set_page_config(
    page_title="Stotra Reader",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define your titles and their corresponding files here
STOTRAS = {
    "Lalitha Sahasranama": {
        "verses": "verses.txt",
        "landing_malayalam": "landing-page-malayalam.txt",
        "landing_sanskrit": "landing-page-sanskrit.txt",
        "end_malayalam": "end-page-malayalam.txt",
        "end_sanskrit": "end-page-sanskrit.txt"
    },
    "Vishnu Sahasranama (Example)": {
        "verses": "vishnu_verses.txt",
        "landing_malayalam": "vishnu_landing_malayalam.txt",
        "landing_sanskrit": "vishnu_landing_sanskrit.txt",
        "end_malayalam": "vishnu_end_malayalam.txt",
        "end_sanskrit": "vishnu_end_sanskrit.txt"
    }
    # Add as many titles as you want here...
}

st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #F8F2E8 !important;
        color: #462A19;
    }
    
    /* Center align container (Card) */
    #swipe-area {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        min-height: 40vh;
        max-width: 720px;
        width: 100%;
        padding: 40px 30px;
        margin: 14px auto 20px auto;
        background: #FFFFFF;
        border-radius: 24px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(0, 0, 0, 0.03);
        position: relative;
        overflow: hidden;
        box-sizing: border-box;
    }
    
    /* Styling for the script text */
    .script-text {
        color: #B8860B;
        font-size: clamp(1.5rem, 4vw, 2.2rem);
        font-weight: 700;
        margin-bottom: 20px;
        line-height: 1.5;
        letter-spacing: 0.2px;
        width: 100%;
        overflow-wrap: break-word;
        word-break: keep-all;
        white-space: pre-wrap;
    }
    
    /* Styling for the English transliteration */
    .english-text {
        color: #3C1D1D;
        font-size: 1.15rem;
        font-style: italic;
        margin-bottom: 24px;
        line-height: 1.6;
        width: 100%;
        word-break: break-word;
        white-space: pre-wrap;
    }
    
    /* Meaning text */
    .meaning-text {
        color: #5A4337;
        font-size: 1.05rem;
        width: 100%;
        margin-top: 10px;
        border-top: 1px solid rgba(100, 65, 18, 0.15);
        padding-top: 24px;
        line-height: 1.6;
        word-break: break-word;
        white-space: pre-wrap;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #FFF6EE !important;
        border-right: 1px solid rgba(72, 39, 17, 0.16) !important;
    }
    
    /* Button styling & Centering */
    .stButton {
        display: flex !important;
        justify-content: center !important;
    }
    .stButton > button {
        background-color: #FFFFFF;
        color: #7A4A1D;
        border: 2px solid #B8860B;
        border-radius: 24px;
        padding: 10px 32px;
        font-size: 1rem;
        transition: all 0.2s ease;
        font-weight: 700;
        min-width: 140px;
    }
    
    .stButton > button:hover {
        background-color: #B8860B;
        color: #FFFFFF;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(184, 134, 11, 0.16);
    }

    /* Page text outside card */
    .info-text {
        color: #8B6A4A;
        font-size: 1rem;
        max-width: 720px;
        margin: 0 auto;
        padding: 0 10px;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent !important;}
    footer {visibility: hidden;}
    
    /* Mobile responsive adjustments */
    @media (max-width: 700px) {
        .block-container { padding-top: 2rem !important; }
        #swipe-area { padding: 30px 20px; border-radius: 20px; }
        .english-text { font-size: 1.05rem; }
        .meaning-text { font-size: 0.95rem; }
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 2. SESSION STATE & SIDEBAR MENU
# ==========================================
st.sidebar.title("🕉️ Menu")

# Title Selection Dropdown
selected_title = st.sidebar.selectbox(
    "Select Title:",
    list(STOTRAS.keys())
)

st.sidebar.divider()

st.sidebar.title("⚙️ Settings")
language_mode = st.sidebar.radio(
    "Select Display Mode:",
    ("Malayalam + English", "Sanskrit + English"),
    index=0
)
show_meaning = st.sidebar.checkbox("📖 Show Meaning", value=True)

# State Management: Reset page to 0 if the user changes the title
if 'current_title' not in st.session_state:
    st.session_state.current_title = selected_title
    st.session_state.page = 0
elif st.session_state.current_title != selected_title:
    st.session_state.current_title = selected_title
    st.session_state.page = 0  # Reset navigation


# ==========================================
# 3. DATA LOADING (Dynamic based on Selection)
# ==========================================
@st.cache_data
def load_app_data(title_name):
    base_dir = Path(__file__).parent
    config = STOTRAS[title_name]
    
    # 1. Load Verses
    verse_file = base_dir / config["verses"]
    if not verse_file.exists():
        return None, None, None, f"Could not find {config['verses']}."
        
    with verse_file.open("r", encoding="utf-8") as f:
        verses = json.load(f)
        
    for verse in verses:
        for field in ("malayalam", "sanskrit", "english", "meaning"):
            if isinstance(verse.get(field), str):
                verse[field] = verse[field].replace("||", "<br>")
                
    # 2. Load Landing Pages
    malayalam_file = base_dir / config["landing_malayalam"]
    sanskrit_file = base_dir / config["landing_sanskrit"]
    
    landing_pages = {
        "Malayalam": malayalam_file.read_text(encoding="utf-8") if malayalam_file.exists() else f"🙏\nWelcome to {title_name}\n(Malayalam page missing)",
        "Sanskrit": sanskrit_file.read_text(encoding="utf-8") if sanskrit_file.exists() else f"🙏\nWelcome to {title_name}\n(Sanskrit page missing)"
    }
    
    # 3. Load End Pages
    end_malayalam_file = base_dir / config["end_malayalam"]
    end_sanskrit_file = base_dir / config["end_sanskrit"]
    
    end_pages = {
        "Malayalam": end_malayalam_file.read_text(encoding="utf-8") if end_malayalam_file.exists() else f"🙏\nEnd of {title_name}\n(Malayalam end missing)",
        "Sanskrit": end_sanskrit_file.read_text(encoding="utf-8") if end_sanskrit_file.exists() else f"🙏\nEnd of {title_name}\n(Sanskrit end missing)"
    }
    
    return verses, landing_pages, end_pages, None

# Load data for the CURRENTLY selected title
verses, landing_pages, end_pages, error_msg = load_app_data(selected_title)

if error_msg:
    st.error(error_msg)
    st.stop()
if not verses:
    st.error(f"The verse file for {selected_title} is empty or misformatted.")
    st.stop()


# ==========================================
# 4. MAIN CONTENT RENDERING
# ==========================================
_, center_col, _ = st.columns([1, 4, 1])

with center_col:
    # Top Information text
    if st.session_state.page == 0:
        st.markdown(f'<div class="info-text">Introduction: {selected_title}</div>', unsafe_allow_html=True)
    elif st.session_state.page == len(verses) + 1:
        st.markdown(f'<div class="info-text">Conclusion: {selected_title}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="info-text">Verse {st.session_state.page} of {len(verses)}</div>', unsafe_allow_html=True)
        
    st.markdown('<div class="info-text" style="margin-bottom: 10px;">Swipe up/down on the card to navigate</div>', unsafe_allow_html=True)

    # Card Content Logic
    if st.session_state.page == 0:
        # --- RENDER LANDING PAGE ---
        selected_lang = "Malayalam" if "Malayalam" in language_mode else "Sanskrit"
        landing_content = landing_pages[selected_lang]
        
        verse_html = f'''
        <div id="swipe-area">
          <div class="script-text" style="margin-bottom: 0;">{landing_content}</div>
        </div>
        '''
    elif st.session_state.page == len(verses) + 1:
        # --- RENDER END PAGE ---
        selected_lang = "Malayalam" if "Malayalam" in language_mode else "Sanskrit"
        end_content = end_pages[selected_lang]
        
        verse_html = f'''
        <div id="swipe-area">
          <div class="script-text" style="margin-bottom: 0;">{end_content}</div>
        </div>
        '''
    else:
        # --- RENDER VERSE ---
        current_verse = verses[st.session_state.page - 1]
        script_text = current_verse['malayalam'] if "Malayalam" in language_mode else current_verse['sanskrit']

        verse_html = f'''
        <div id="swipe-area">
          <div class="script-text">{script_text}</div>
          <div class="english-text">{current_verse['english']}</div>
          {f'<div class="meaning-text">✨ {current_verse["meaning"]}</div>' if show_meaning else ''}
        </div>
        '''
        
    st.markdown(verse_html, unsafe_allow_html=True)


# ==========================================
# 5. NAVIGATION BUTTONS
# ==========================================
col1, col2, col3, col4, col5 = st.columns([1, 1.5, 0.3, 1.5, 1])

with col2:
    if st.button("← Previous", key="prev_btn", disabled=(st.session_state.page == 0)):
        st.session_state.page -= 1
        st.rerun()

with col4:
    if st.button("Next →", key="next_btn", disabled=(st.session_state.page == len(verses) + 1)):
        st.session_state.page += 1
        st.rerun()


# ==========================================
# 6. JAVASCRIPT GESTURE LISTENER
# ==========================================
st.markdown(
    """
    <script>
    (function(){
        const doc = window.parent.document || document;
        let isThrottled = false;

        function clickVisibleButton(direction) {
            if (isThrottled) return;

            const allButtons = Array.from(doc.querySelectorAll('button'));
            const targetBtn = allButtons.find(btn => btn.innerText.includes(direction));
            
            if (targetBtn && !targetBtn.disabled) {
                isThrottled = true;
                targetBtn.click();
                setTimeout(() => { isThrottled = false; }, 800);
            }
        }

        doc.addEventListener('keydown', function(evt) {
            if (["ArrowRight", "ArrowDown", "PageDown", " "].includes(evt.key)) {
                evt.preventDefault(); 
                clickVisibleButton('Next');
            } else if (["ArrowLeft", "ArrowUp", "PageUp"].includes(evt.key)) {
                evt.preventDefault();
                clickVisibleButton('Previous');
            }
        }, {passive: false});

        doc.addEventListener('wheel', function(evt) {
            if (evt.deltaY > 50) clickVisibleButton('Next');
            else if (evt.deltaY < -50) clickVisibleButton('Previous');
        }, {passive: true});

        let touchStartY = 0;
        doc.addEventListener('touchstart', function(evt) {
            touchStartY = evt.changedTouches[0].screenY;
        }, {passive: true});

        doc.addEventListener('touchend', function(evt) {
            let touchEndY = evt.changedTouches[0].screenY;
            let diff = touchStartY - touchEndY;
            
            if (diff > 60) clickVisibleButton('Next');
            else if (diff < -60) clickVisibleButton('Previous');
        }, {passive: true});

    })();
    </script>
    """,
    unsafe_allow_html=True
)