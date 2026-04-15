import os
import re
from pathlib import Path
from typing import Optional

import lyricsgenius
from dotenv import load_dotenv 

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

def _clean_title(title: str) -> str:     #cleanup
    cleaned = title.strip()
    cleaned = re.sub(r"\s*[\(\[\{][^)\]\}]*?(remaster|live|version|edit|mix)[^)\]\}]*?[\)\]\}]\s*", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*-\s*(live|.*remaster(ed)?|radio edit|mono|stereo)\b.*$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def fetch_lyrics(artist: str, title: str) -> Optional[str]:
    if not artist or not title:
        return None

    token = GENIUS_ACCESS_TOKEN.strip()
    if not token:
        print("Debug: No Genius Token found!")
        return None

    cleaned_title = _clean_title(title)

    try:
        genius = lyricsgenius.Genius(token)
        song = genius.search_song(cleaned_title, artist)
        
        if not song:
            song = genius.search_song(cleaned_title, artist.split(',')[0])

        if song and song.lyrics:
            lyrics = song.lyrics
            lyrics = re.sub(r'^.*Lyrics', '', lyrics)
            lyrics = re.sub(r'\d*Embed$', '', lyrics)
            return lyrics.strip()
            
    except Exception as e:
        print(f"Genius API Error: {e}")
        return None
    
    return None