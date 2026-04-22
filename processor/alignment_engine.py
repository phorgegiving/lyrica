from __future__ import annotations

import os
import sys
import shutil
import imageio_ffmpeg

import json
import re
from pathlib import Path
from typing import Dict, List

import whisperx
import torch


WHISPER_MODEL = "small"

if sys.platform == 'win32': #костыль, увы
    venv_site_packages = os.path.join(os.path.dirname(sys.executable), "Lib", "site-packages")
    cuda_libs = [
        os.path.join(venv_site_packages, "nvidia", "cublas", "bin"),
        os.path.join(venv_site_packages, "nvidia", "cudnn", "bin"),
    ]
    for path in cuda_libs:
        if os.path.exists(path):
            os.add_dll_directory(path)
            print(f"Added DLL directory: {path}")

def _ensure_ffmpeg_on_path() -> None:
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)

    target = os.path.join(ffmpeg_dir, "ffmpeg.exe")
    if not os.path.exists(target):
        shutil.copy2(ffmpeg_exe, target)

    if ffmpeg_dir not in os.environ["PATH"]:
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]

def _detect_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"

def _clean_lyrics(raw_text: str) -> str:
    cleaned = re.sub(r"\[[^\]]*\]", "", raw_text)  # remove [Verse], [Chorus] etc
    cleaned = re.sub(r"\n\s*\n+", "\n", cleaned)
    return cleaned.strip()

def _match_lyrics_to_segments(
    transcribed_segments: List[Dict],
    lyrics_lines: List[str],
) -> List[Dict]:

    if not transcribed_segments or not lyrics_lines:
        return transcribed_segments

    result = []
    seg_count = len(transcribed_segments)
    line_count = len(lyrics_lines)

    for i, segment in enumerate(transcribed_segments):
        #пропорционально маппим строку на сегмент
        line_idx = round(i * line_count / seg_count)
        line_idx = min(line_idx, line_count - 1)
        result.append({
            "text": lyrics_lines[line_idx],
            "start": segment["start"],
            "end": segment["end"],
        })

    return result

def align_lyrics(audio_path: str | Path, text_path: str | Path) -> Path:
    audio_file = Path(audio_path)
    lyrics_file = Path(text_path)

    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not lyrics_file.exists():
        raise FileNotFoundError(f"Lyrics file not found: {lyrics_file}")

    output_path = audio_file.parent / "alignment.json"
    if output_path.exists():
        print("alignment.json already exists, skipping.")
        return output_path

    lyrics = _clean_lyrics(lyrics_file.read_text(encoding="utf-8"))
    if not lyrics:
        raise ValueError("Lyrics file is empty after cleaning.")
    lyrics_lines = [line.strip() for line in lyrics.splitlines() if line.strip()]

    device = _detect_device()
    _ensure_ffmpeg_on_path()

    compute_type = "float16" if device == "cuda" else "int8"
    model = whisperx.load_model(WHISPER_MODEL, device=device, compute_type=compute_type)
    audio = whisperx.load_audio(str(audio_file))

    detection = model.transcribe(audio, batch_size=16)
    language_code = detection.get("language")
    if not language_code:
        raise RuntimeError("Could not detect language from audio.")
    print(f"Detected language: {language_code}, segments: {len(detection['segments'])}")

    segments = _match_lyrics_to_segments(detection["segments"], lyrics_lines)

    align_model, align_metadata = whisperx.load_align_model(
        language_code=language_code,
        device=device,
    )
    aligned = whisperx.align(
        segments,
        align_model,
        align_metadata,
        audio,
        device,
    )

    words: List[Dict] = []
    for word_data in aligned.get("word_segments", []):
        word = word_data.get("word")
        start = word_data.get("start")
        end = word_data.get("end")
        if not word or start is None or end is None:
            continue
        words.append({"word": word, "start": float(start), "end": float(end)})

    output_path.write_text(
        json.dumps(words, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved {len(words)} word alignments to: {output_path}")
    return output_path