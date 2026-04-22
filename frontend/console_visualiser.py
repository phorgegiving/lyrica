import asyncio
import json
import time
from pathlib import Path
from typing import Optional, Tuple

_active_task: Optional[asyncio.Task] = None
_active_track: Optional[Tuple[str, str]] = None


def stop_visualiser() -> None:
    global _active_task, _active_track
    if _active_task is not None and not _active_task.done():
        _active_task.cancel()
    _active_task = None
    _active_track = None


async def _run_visualiser(file_path: Path, entry_point: float, track_key: Tuple[str, str]) -> None:
    global _active_track
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: File not found.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    data.sort(key=lambda x: x["start"])
    print("--- Starting Playback ---\n")
    start_clock = time.time()

    for entry in data:
        if _active_track != track_key:
            return

        word = entry.get("word")
        target_time = entry.get("start")

        if word is None or target_time is None or target_time < entry_point:
            continue

        relative_target = target_time - entry_point
        current_elapsed = time.time() - start_clock
        wait_time = relative_target - current_elapsed

        if wait_time > 0:
            await asyncio.sleep(wait_time)

        if _active_track != track_key:
            return
        print(f"[{target_time:.3f}s] {word}")


def visualise(file_path: Path, entry_point: str | int, track_key: Tuple[str, str]) -> None:
    global _active_task, _active_track
    entry_point_seconds = float(entry_point)

    if _active_task is not None and not _active_task.done():
        _active_task.cancel()

    _active_track = track_key
    _active_task = asyncio.create_task(
        _run_visualiser(Path(file_path), entry_point_seconds, track_key)
    )