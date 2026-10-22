#!/usr/bin/env python3
"""Generate an MP3 via ACE Music hosted chat-completions API."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://api.acemusic.ai/v1/chat/completions"
MODEL = "acemusic/acestep-v1.5-turbo"


def load_key() -> str:
    key = os.environ.get("ACE_MUSIC_API_KEY", "").strip()
    if key:
        return key
    path = os.environ.get("ACE_MUSIC_API_KEY_FILE", "").strip()
    if path:
        return Path(path).expanduser().read_text(encoding="utf-8").strip()
    # Grok Bot box convention (optional)
    box = Path("/home/box/agent-data/secrets/ACE_MUSIC_API_KEY")
    if box.is_file():
        return box.read_text(encoding="utf-8").strip()
    raise SystemExit(
        "Missing ACE Music API key. Set ACE_MUSIC_API_KEY or ACE_MUSIC_API_KEY_FILE "
        "(see SKILL.md Prerequisites)."
    )


def extract_data_url(payload: dict) -> str:
    msg = (payload.get("choices") or [{}])[0].get("message") or {}
    audio = msg.get("audio")
    if isinstance(audio, list) and audio:
        item = audio[0] or {}
        url = ((item.get("audio_url") or {}).get("url")) or item.get("url")
        if url:
            return url
    if isinstance(audio, dict):
        url = ((audio.get("audio_url") or {}).get("url")) or audio.get("url")
        if url:
            return url
    raw = json.dumps(payload)
    m = re.search(r"data:audio/[^;]+;base64,([A-Za-z0-9+/=]+)", raw)
    if m:
        return "data:audio/mpeg;base64," + m.group(1)
    raise SystemExit("No audio data_url in API response")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prompt", help="Music description")
    ap.add_argument("--prompt-file", type=Path, help="UTF-8 file with the prompt")
    ap.add_argument("--output", type=Path, required=True, help="Output .mp3 path")
    ap.add_argument("--duration", type=float, default=30.0)
    ap.add_argument("--instrumental", action="store_true", default=True)
    ap.add_argument("--with-vocals", action="store_true", help="Allow vocals")
    ap.add_argument("--bpm", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--timeout", type=float, default=180.0)
    args = ap.parse_args()

    if args.prompt_file:
        prompt = args.prompt_file.read_text(encoding="utf-8").strip()
    else:
        prompt = (args.prompt or "").strip()
    if not prompt:
        raise SystemExit("Provide --prompt or --prompt-file")

    instrumental = not args.with_vocals
    audio_config: dict = {
        "duration": args.duration,
        "format": "mp3",
        "instrumental": instrumental,
    }
    if args.bpm is not None:
        audio_config["bpm"] = args.bpm

    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["audio"],
        "instrumental": instrumental,
        "lyrics": "" if instrumental else None,
        "audio_config": audio_config,
    }
    # drop null lyrics
    body = {k: v for k, v in body.items() if v is not None}

    if args.dry_run:
        print(
            json.dumps(
                {
                    "ok": True,
                    "dry_run": True,
                    "url": API_URL,
                    "model": MODEL,
                    "output": str(args.output),
                    "prompt_chars": len(prompt),
                    "audio_config": audio_config,
                },
                ensure_ascii=False,
            )
        )
        return

    key = load_key()
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "ace-music-skill/1.0 (+https://github.com/yoursun0/skills)",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        raise SystemExit(f"HTTP {e.code}: {detail}") from e

    data_url = extract_data_url(payload)
    if not data_url.startswith("data:"):
        raise SystemExit("Expected data: URL for audio")
    b64 = data_url.split(",", 1)[1]
    out = args.output.expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(b64))

    msg = (payload.get("choices") or [{}])[0].get("message") or {}
    content = (msg.get("content") or "")[:800]
    print(
        json.dumps(
            {
                "ok": True,
                "output": str(out.resolve()),
                "bytes": out.stat().st_size,
                "metadata_preview": content,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
