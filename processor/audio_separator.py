from __future__ import annotations

import os
import shutil
import time
from pathlib import Path
from typing import Tuple

import imageio_ffmpeg
from audio_separator.separator import Separator


FAST_MODEL = "UVR-MDX-NET-Inst_HQ_3.onnx"

def _ensure_ffmpeg_on_path() -> None:
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)
    
    target = os.path.join(ffmpeg_dir, "ffmpeg.exe")
    if not os.path.exists(target):
        shutil.copy2(ffmpeg_exe, target)
    
    if ffmpeg_dir not in os.environ["PATH"]:
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]


def get_vocals(input_path: str | Path, output_dir: str | Path) -> Tuple[Path, Path]:
    source = Path(input_path)
    cache_dir = Path(output_dir)
    vocals_target = cache_dir / "vocals.wav"
    instrumental_target = cache_dir / "instrumental.wav"

    if not source.exists():
        raise FileNotFoundError(f"Input audio file does not exist: {source}")

    cache_dir.mkdir(parents=True, exist_ok=True)

    _ensure_ffmpeg_on_path()  # <-- inject before Separator is instantiated

    separator = Separator(output_dir=str(cache_dir))
    separator.load_model(model_filename=FAST_MODEL)

    start_time = time.perf_counter()
    separator.separate(str(source))
    elapsed_seconds = time.perf_counter() - start_time
    print(f"Separation completed in {elapsed_seconds:.2f} seconds.")

    if not vocals_target.exists() or not instrumental_target.exists():
        raise RuntimeError(
            "Track separation finished, but expected vocals.wav or instrumental.wav is missing."
        )

    return vocals_target, instrumental_target