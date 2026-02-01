#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate TTS for a Twi phrase and play it (Windows).
Usage:
  python play_twi_phrase.py
  python play_twi_phrase.py "Dɛn na woyɛ?"
  python play_twi_phrase.py "Ɛhe na Cultiflow wɔ"
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_WAV = PROJECT_ROOT / "sounds" / "custom" / "play_phrase.wav"

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except Exception:
    pass

from voice_assistant import get_api_key, text_to_speech


def main():
    phrase = "Dɛn na woyɛ?"
    if len(sys.argv) > 1:
        phrase = " ".join(sys.argv[1:]).strip() or phrase

    print(f"Generating Twi TTS: {phrase!r}")
    api_key = get_api_key()
    path, _ = text_to_speech(phrase, api_key, str(OUTPUT_WAV), lang="tw")
    if not path:
        print("TTS failed. Check API key and ghana-nlp.")
        sys.exit(1)

    print(f"Playing: {path}")
    try:
        import winsound
        winsound.PlaySound(path, winsound.SND_FILENAME)
    except Exception as e:
        print(f"Playback failed: {e}")
        print(f"Open manually: {path}")
        sys.exit(1)
    print("Done.")


if __name__ == "__main__":
    main()
