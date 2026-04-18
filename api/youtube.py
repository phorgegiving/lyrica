from pathlib import Path

from yt_dlp import YoutubeDL

import imageio_ffmpeg

ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()  # path to bundled ffmpeg binary

def download_audio(artist: str, title: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_base = output_path.with_suffix("")
    query = f"ytsearch1:{artist} - {title}"
    ydl_opts = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "outtmpl": str(output_base) + ".%(ext)s",
    "quiet": True,
    "no_warnings": True,
    "ffmpeg_location": ffmpeg_path,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([query])

    return output_path