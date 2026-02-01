#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translate English DB questions to Twi and print a cheat sheet.
No Twi is added to the DB – English only. Use these Twi phrases when you call.
Run: python twi_questions_cheatsheet.py
"""
import os
from pathlib import Path

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except Exception:
    pass

from database import get_db
from voice_assistant import translate_text, get_api_key

def main():
    api_key = get_api_key()
    db_path = str(Path(__file__).resolve().parent / "voice_assistant.db")
    db = get_db(db_path)
    pairs = db.get_all_qa_pairs(language="en", limit=200)

    # Dedupe by (question, answer) to avoid translating same Q multiple times
    seen = set()
    unique = []
    for qa in pairs:
        k = (qa["question_text"].strip(), qa["answer_text"].strip())
        if k in seen:
            continue
        seen.add(k)
        unique.append(qa)

    out_path = Path(__file__).resolve().parent / "TWI_QUESTIONS_CHEATSHEET.txt"
    lines = [
        "Say this in Twi when you call (DB stays English-only)",
        "=" * 60,
        "",
    ]

    for qa in unique:
        q_en = qa["question_text"].strip()
        a_en = (qa["answer_text"] or "").strip()
        # Strip trailing ?!., sometimes helps translation API
        q_for_translate = q_en.rstrip("?!.,;:")
        twi, _ = translate_text(q_for_translate or q_en, "en-tw", api_key)
        twi = (twi or "(translation failed)").strip()
        lines.append(f"  Say (Twi):  {twi}")
        lines.append(f"  English:    {q_en}")
        lines.append("")

    text = "\n".join(lines)
    out_path.write_text(text, encoding="utf-8")
    print(text)
    print("=" * 60)
    print(f"Saved to: {out_path}")

if __name__ == "__main__":
    main()
