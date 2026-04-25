from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import librosa
import numpy as np


def _to_float(value: Any) -> float:
    if isinstance(value, np.ndarray):
        if value.size == 0:
            return 0.0
        return float(value.reshape(-1)[0])
    return float(value)


def _to_float_list(values: np.ndarray) -> List[float]:
    return [float(v) for v in values.tolist()]


def analyze_audio(audio_path: str | Path) -> Path:
    audio_file = Path(audio_path)
    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    y, sr = librosa.load(str(audio_file), sr=None, mono=True)

    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    print(tempo, " bpm")

    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units="frames")
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    rhythm_data: Dict[str, Any] = {
        "bpm": _to_float(tempo),
        "beats": _to_float_list(beat_times),
        "onsets": _to_float_list(onset_times),
    }

    output_path = audio_file.parent / "rhythm.json"
    output_path.write_text(
        json.dumps(rhythm_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path
