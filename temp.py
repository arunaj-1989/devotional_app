# code to update the "meaning" key in verses.txt from "meaning.txt" file
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSES_PATH = Path("verses.txt")
MEANINGS_PATH = Path("meaning.txt")

# for each id in "meaning.txt", update the corresponding verse  "meaning" key in "verses.txt" with the meaning key from "meaning.txt".
with MEANINGS_PATH.open("r", encoding="utf-8") as f:
    meanings = json.load(f)
with VERSES_PATH.open("r", encoding="utf-8") as f:
    verses = json.load(f)
for m in meanings:
    for v in verses:
        if v["id"] == m["id"]:
            v["meaning"] = m["meaning"]
with VERSES_PATH.open("w", encoding="utf-8") as f:
    json.dump(verses, f, ensure_ascii=False, indent=2)
    
