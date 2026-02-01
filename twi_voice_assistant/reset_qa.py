#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clear all Q&A pairs and seed a new set.
Run: python reset_qa.py
"""
import sqlite3
from pathlib import Path

from database import get_db

DB_PATH = Path(__file__).resolve().parent / "voice_assistant.db"

# New Q&A set (question, answer) - all English
SEED = [
    ("What is Cultiflow?", "Cultiflow is a technology company in Ghana. We build voice assistants and software."),
    ("What services do you offer?", "We offer voice assistants, IVR systems, and business software solutions."),
    ("Where are you located?", "We are based in Accra, Ghana."),
    ("What is the company name?", "The company name is Cultiflow."),
    ("How can I reach you?", "You can call this number or email info@cultiflow.com."),
    ("Who runs Cultiflow?", "Cultiflow is run by the Cultiflow team."),
    ("What do you do?", "We build voice assistants, IVR systems, and business software."),
    ("what you do", "We build voice assistants, IVR systems, and business software."),
    ("what does you do", "We build voice assistants, IVR systems, and business software."),
    ("what do we do", "We build voice assistants, IVR systems, and business software."),
    ("what does cultiflow do", "We build voice assistants, IVR systems, and business software."),
    ("Where is Cultiflow?", "Cultiflow is based in Ghana."),
    ("How can I contact you?", "Call this number or visit the Cultiflow website."),
]

def main():
    db_path = str(DB_PATH)
    print(f"Database: {db_path}")

    # Clear qa_pairs (SQLite)
    conn = sqlite3.connect(db_path)
    cur = conn.execute("SELECT COUNT(*) FROM qa_pairs")
    n = cur.fetchone()[0]
    conn.execute("DELETE FROM qa_pairs")
    conn.commit()
    conn.close()
    print(f"Cleared {n} Q&A pair(s).")

    # Seed new set
    db = get_db(db_path)
    for q, a in SEED:
        db.add_qa_pair(q, a, language="en")
        preview = a if len(a) <= 50 else a[:50] + "..."
        print(f"  + {q!r} -> {preview}")
    print(f"\nSeeded {len(SEED)} Q&A pairs. Done.")

if __name__ == "__main__":
    main()
