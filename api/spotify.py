import asyncio
import sys
from pathlib import Path

from typing import Any, Dict, Optional

from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager

try:
    from config import POLL_INTERVAL, DEBUG_ACTIVE
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from config import POLL_INTERVAL, DEBUG_ACTIVE


async def get_media_info() -> Optional[Dict[str, str]]:
    try:
        manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
        if manager is None:
            return None

        session = manager.get_current_session()
        if session is None:
            return None

        media_properties = await session.try_get_media_properties_async()
        playback_info = session.get_playback_info()
        status_value: Any = getattr(playback_info, "playback_status", None)

        status_name = getattr(status_value, "name", str(status_value))
        if status_name not in {"Playing", "Paused"}:
            status_name = "Paused" if "paused" in status_name.lower() else "Playing" if "playing" in status_name.lower() else status_name

        title = (media_properties.title or "").strip()
        artist = (media_properties.artist or "").strip()

        return {
            "title": title or "Unknown Title",
            "artist": artist or "Unknown Artist",
            "playback_status": status_name,
        }
    except Exception:
        # fallback
        return None


async def watch_media_changes(poll_interval: float = POLL_INTERVAL, debug: bool = DEBUG_ACTIVE) -> None:
    previous_signature: Optional[tuple[str, str, str]] = None
    had_session = True

    while True:
        media_info = await get_media_info()

        if media_info is None:
            if had_session:
                print("No active media session.")
                had_session = False
                previous_signature = None
        else:
            had_session = True
            current_signature = (
                media_info["title"],
                media_info["artist"],
                media_info["playback_status"],
            )

            if current_signature != previous_signature:
                if debug:
                    print(
                        f'Currently playing: {media_info["title"]} '
                        f'by {media_info["artist"]}. '
                        f'Status: {media_info["playback_status"]}'
                    )
                previous_signature = current_signature

        await asyncio.sleep(poll_interval)


if __name__ == "__main__":
    try:
        asyncio.run(watch_media_changes())
    except KeyboardInterrupt:
        print("Stopped media watcher.")