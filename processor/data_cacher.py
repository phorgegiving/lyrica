import re
from pathlib import Path
from typing import Optional, Tuple

from api.genius import download_cover_image, fetch_song_data
from api.youtube import download_audio
from processor.audio_separator import get_vocals
from processor.alignment_engine import align_lyrics

from colorthief import ColorThief

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
    instrumental_path = song_dir / "instrumental.wav"
    aligned_path = song_dir / "alignment.json"
    vocals_path = song_dir / "vocals.wav"
    cover_path = song_dir / "cover.jpg"

    song_dir.mkdir(parents=True, exist_ok=True)
    audio_path.parent.mkdir(parents=True, exist_ok=True)

    lyrics: str = ""
    need_lyrics = not lyrics_path.exists()
    need_cover = not cover_path.exists()
    fetched_lyrics: Optional[str] = None
    cover_url: Optional[str] = None

    if need_lyrics or need_cover:
        fetched_lyrics, cover_url = fetch_song_data(artist, title)

    if lyrics_path.exists():
        print("Lyrics found.")
        lyrics = lyrics_path.read_text(encoding="utf-8")
    else:
        print("Lyrics not found, downloading...")
        lyrics = fetched_lyrics or ""
        lyrics_path.write_text(lyrics, encoding="utf-8")

    if cover_path.exists():
        print("Cover found.")
    else:
        print("Cover not found, downloading...")
        if cover_url:
            download_cover_image(cover_url, cover_path)
        else:
            print("Cover URL not found in Genius response.")

    if audio_path.exists():
        print("Audio found.")
    else:
        print("Audio not found, downloading...")
        audio_path = download_audio(artist, title, audio_path)

    if instrumental_path.exists() and vocals_path.exists():
        print("Vocals and Instrumental (separated) exist.")
    else:
        print("Vocals and instrumental not found, separating...")
        get_vocals(audio_path, song_dir)

    if aligned_path.exists():
        print("alignment.json exists.")
    elif not lyrics_path.read_text(encoding="utf-8"):
        print("Couldnt find alignment.json, the song is instrumental/lyrics do not exist.")
    else:
        print("Couldnt find alignment.json, aligning...")
        align_lyrics(vocals_path, lyrics_path)

    return lyrics, audio_path
