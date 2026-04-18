import re
from pathlib import Path
from typing import Optional, Tuple, Union

from api.genius import fetch_lyrics
from api.youtube import download_audio

def _slugify(value: str) -> str:
    normalized = value.strip().lower()
    normalized = re.sub(r"\s+", "_", normalized)
    normalized = re.sub(r"[^a-z0-9_\-]", "", normalized)
    return normalized.strip("_")

def get_song_data(artist: str, title: str) -> Tuple[str, Path]:
    folder_name = _slugify(f"{artist} {title}")
    song_dir = Path("data") / folder_name
    lyrics_path = song_dir / "lyrics.txt"
    audio_path = song_dir / "song.mp3"

    song_dir.mkdir(parents=True, exist_ok=True)
    audio_path.parent.mkdir(parents=True, exist_ok=True)

    if lyrics_path.exists():
        print("Lyrics found.")
        lyrics = lyrics_path.read_text(encoding="utf-8")
    else:
        print("Lyrics not found, downloading...")
        lyrics_result: Optional[str] = fetch_lyrics(artist, title)
        lyrics = lyrics_result or ""
        lyrics_path.write_text(lyrics, encoding="utf-8")

    if audio_path.exists():
        print("Audio found.")
    else:
        print("Audio not found, downloading...")
        audio_path = download_audio(artist, title, audio_path)

    return lyrics, audio_path
