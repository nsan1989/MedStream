import argparse
import shutil
import subprocess
import time
from typing import Any, Dict, Optional

import requests


def to_absolute_url(base_url: str, raw_url: str) -> str:
    if raw_url.startswith("http://") or raw_url.startswith("https://"):
        return raw_url
    return f"{base_url.rstrip('/')}/{raw_url.lstrip('/')}"


class DeviceAgent:
    def __init__(self, base_url: str, device_id: str, poll_seconds: int = 5) -> None:
        self.base_url = base_url.rstrip("/")
        self.device_id = device_id
        self.poll_seconds = poll_seconds
        self.last_command_id: Optional[str] = None
        self.session = requests.Session()
        self.ffplay = shutil.which("ffplay")

    @property
    def next_command_url(self) -> str:
        return f"{self.base_url}/device/player/{self.device_id}/next-command/"

    @property
    def ack_url(self) -> str:
        return f"{self.base_url}/device/player/{self.device_id}/ack/"

    def send_ack(self, command_id: str, status: str, message: str) -> None:
        payload = {
            "command_id": command_id,
            "status": status,
            "message": message,
        }
        try:
            self.session.post(self.ack_url, json=payload, timeout=10)
        except requests.RequestException as exc:
            print(f"[ACK ERROR] {exc}")

    def poll_once(self) -> None:
        try:
            response = self.session.get(self.next_command_url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            print(f"[POLL ERROR] {exc}")
            return
        except ValueError:
            print("[POLL ERROR] Invalid JSON response.")
            return

        command_id = data.get("command_id")
        payload = data.get("payload") or {}
        if not command_id or payload.get("command") != "PLAY":
            return

        if command_id == self.last_command_id:
            return

        self.last_command_id = command_id
        source_type = payload.get("source_type")

        if source_type == "MEDIA_ASSET":
            ok = self.play_media_asset(payload)
            self.send_ack(
                command_id,
                "PLAYED" if ok else "FAILED",
                "Media playback executed." if ok else "Media playback failed.",
            )
        elif source_type == "PLAYLIST":
            ok = self.play_playlist(payload)
            self.send_ack(
                command_id,
                "PLAYED" if ok else "FAILED",
                "Playlist playback executed." if ok else "Playlist playback failed.",
            )
        else:
            self.send_ack(command_id, "FAILED", "Unknown source type.")

    def play_media_asset(self, payload: Dict[str, Any]) -> bool:
        file_url = payload.get("file_url")
        media_type = (payload.get("media_type") or "").upper()
        title = payload.get("title", "Untitled")

        if not file_url:
            print("[PLAY ERROR] Missing file URL.")
            return False

        media_url = to_absolute_url(self.base_url, file_url)
        print(f"[PLAY] {title} ({media_type}) -> {media_url}")

        return self.play_with_ffplay(media_url, media_type, duration=10)

    def play_playlist(self, payload: Dict[str, Any]) -> bool:
        items = payload.get("items") or []
        if not items:
            print("[PLAY ERROR] Playlist has no items.")
            return False

        print(
            f"[PLAYLIST] {payload.get('playlist_name', 'Untitled')} ({len(items)} items)"
        )
        for item in items:
            media_url = to_absolute_url(self.base_url, item.get("file_url", ""))
            media_type = (item.get("media_type") or "").upper()
            duration = int(item.get("duration") or 10)
            title = item.get("title", "Untitled")

            print(f"  -> {title} ({media_type}) for {duration}s")
            ok = self.play_with_ffplay(media_url, media_type, duration=duration)
            if not ok:
                return False
        return True

    def play_with_ffplay(self, media_url: str, media_type: str, duration: int) -> bool:
        if not self.ffplay:
            print(
                "[PLAY ERROR] ffplay not found. Install FFmpeg and ensure ffplay is on PATH."
            )
            return False

        cmd = [self.ffplay, "-loglevel", "error", "-nostats", "-fs"]

        if media_type == "IMAGE":
            cmd.extend(["-loop", "0", "-t", str(max(1, duration))])
        elif media_type == "VIDEO":
            # Videos should auto close when done
            cmd.append("-autoexit")

        cmd.append(media_url)

        try:
            print(f"[FFPLAY CMD] {' '.join(cmd)}")
            result = subprocess.run(cmd, check=False)
            return result.returncode == 0
        except Exception as exc:
            print(f"[PLAY ERROR] {exc}")
            return False

    def run(self) -> None:
        print(f"[AGENT] Starting for device {self.device_id}")
        print(f"[AGENT] Polling {self.next_command_url} every {self.poll_seconds}s")
        while True:
            self.poll_once()
            time.sleep(self.poll_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MedStream device playback agent")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--poll-seconds", type=int, default=5)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    agent = DeviceAgent(
        base_url=args.base_url,
        device_id=args.device_id,
        poll_seconds=args.poll_seconds,
    )
    agent.run()
