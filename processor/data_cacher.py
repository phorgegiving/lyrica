import shutil
import re
from pathlib import Path
from typing import Optional, Tuple, Union

from api.genius import fetch_lyrics

def _slugify(value: str) -> str:
    normalized = value.strip().lower()
    normalized = re.sub(r"\s+", "_", normalized)
    normalized = re.sub(r"[^a-z0-9_\-]", "", normalized)
    return normalized.strip("_")

def get_song_data(artist: str, title: str) -> Tuple[str, Path]:
    folder_name = _slugify(f"{artist} {title}")
    song_dir = Path("data") / folder_name
    lyrics_path = song_dir / "lyrics.txt"

    if song_dir.exists():
        print("[Cache] Song found, loading...")
        lyrics = lyrics_path.read_text(encoding="utf-8") if lyrics_path.exists() else ""
        return lyrics #TODO: add audio here
    
    print(f'New song detected, downloading lyrics...')
    song_dir.mkdir(parents=True, exist_ok=True)

    lyrics: Optional[str] = fetch_lyrics(artist, title)
    lyrics_path.write_text(lyrics or "", encoding="utf-8")

    return lyrics or "" #audio later too
