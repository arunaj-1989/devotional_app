#!/usr/bin/env python3
"""Fetch Rasikas printable page and update verses.txt meanings for ids present."""
import re
import json
from pathlib import Path
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://web.archive.org/web/20140317010626/http://rasikas.org/mw/index.php?title=Lalitha_Sahasranamam&printable=yes"
ROOT = Path(__file__).resolve().parents[1]
VERSes_PATH = ROOT / "verses.txt"


def fetch_printable():
    r = requests.get(BASE_URL, timeout=30)
    r.raise_for_status()
    return r.text


def extract_meanings(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    # Find the headline element with text 'Meanings'
    headline = None
    for el in soup.find_all(class_='mw-headline'):
        if el.get_text(strip=True).lower() == 'meanings':
            headline = el
            break
    meanings = {}
    if headline:
        # Find the next ordered list (ol) which contains meanings as list items
        parent = headline.parent
        ol = None
        for sib in parent.find_next_siblings():
            if sib.name == 'ol':
                ol = sib
                break
        if ol:
            li_items = ol.find_all('li', recursive=False)
            for idx, li in enumerate(li_items, start=1):
                text = ' '.join(line.strip() for line in li.get_text('\n').splitlines())
                text = re.sub(r"\s+", ' ', text).strip()
                meanings[idx] = text
            return meanings
    # Fallback: try regex on full text
    full = soup.get_text('\n')
    pattern = re.compile(r"^\s*(\d{1,4})\.\s*(.+?)(?=^\s*\d{1,4}\.\s|\Z)", re.M | re.S)
    for m in pattern.finditer(full):
        num = int(m.group(1))
        text = ' '.join(line.strip() for line in m.group(2).splitlines())
        text = re.sub(r"\s+", ' ', text).strip()
        meanings[num] = text
    return meanings


def load_verses():
    with VERSes_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)


def save_verses(data):
    with VERSes_PATH.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_meanings(verses, meanings_map, max_id=182):
    count = 0
    for v in verses:
        vid = v.get('id')
        if not isinstance(vid, int):
            continue
        if vid <= max_id and vid in meanings_map:
            v['meaning'] = meanings_map[vid]
            count += 1
    return count


def main():
    print('Fetching Rasikas printable page...')
    html = fetch_printable()
    print('Extracting meanings...')
    meanings = extract_meanings(html)
    if not meanings:
        print('No meanings found; aborting.')
        return
    print(f'Parsed {len(meanings)} meanings; updating verses.txt...')
    verses = load_verses()
    updated = update_meanings(verses, meanings, max_id=182)
    save_verses(verses)
    print(f'Updated {updated} verse meanings in {VERSes_PATH}')


if __name__ == '__main__':
    main()
