#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q&A Store - Dual backend (PostgreSQL + SQLite)
When a caller asks a question, answers are looked up from both databases.
Lookup: PostgreSQL first, then SQLite. Writes: both.
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

# PostgreSQL driver (optional)
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


def _row_to_dict(row, keys: List[str]) -> Dict:
    """Convert DB row to dict with given keys."""
    if row is None:
        return None
    if hasattr(row, "keys"):
        return dict(row)
    return dict(zip(keys, row)) if keys else {}


class QAStore:
    """
    Q&A storage using PostgreSQL and SQLite.
    - Lookup: PostgreSQL first, then SQLite (fallback).
    - Add/Update: write to both.
    """

    QA_KEYS = [
        "qa_id", "question_text", "answer_text", "language",
        "usage_count", "last_used", "created_at", "updated_at",
    ]

    def __init__(
        self,
        sqlite_path: str = "voice_assistant.db",
        postgres_uri: Optional[str] = None,
    ):
        self.sqlite_path = Path(sqlite_path)
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        self.postgres_uri = postgres_uri or os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URI")
        self._sqlite: Optional[sqlite3.Connection] = None
        self._pg = None
        self._pg_available = False
        self._sqlite_available = True
        self._init_backends()

    def _init_backends(self):
        # SQLite
        try:
            self._sqlite = sqlite3.connect(str(self.sqlite_path))
            self._sqlite.row_factory = sqlite3.Row
            self._init_sqlite_schema()
        except Exception as e:
            print(f"WARNING: SQLite Q&A store init failed: {e}", flush=True)
            self._sqlite_available = False

        # PostgreSQL
        if self.postgres_uri and PSYCOPG2_AVAILABLE:
            try:
                self._pg = psycopg2.connect(self.postgres_uri)
                self._init_postgres_schema()
                self._pg_available = True
                print("Q&A store: PostgreSQL connected.", flush=True)
            except Exception as e:
                print(f"WARNING: PostgreSQL Q&A store init failed: {e}", flush=True)
                self._pg_available = False
        else:
            if not PSYCOPG2_AVAILABLE:
                print("WARNING: psycopg2 not installed. PostgreSQL Q&A disabled.", flush=True)
            elif not self.postgres_uri:
                print("Q&A store: PostgreSQL not configured (no DATABASE_URL/POSTGRES_URI).", flush=True)

        if not self._sqlite_available and not self._pg_available:
            raise RuntimeError("At least one of SQLite or PostgreSQL must be available for Q&A store.")

    def _init_sqlite_schema(self):
        cur = self._sqlite.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS qa_pairs (
                qa_id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL,
                answer_text TEXT NOT NULL,
                language TEXT DEFAULT 'tw',
                usage_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(question_text, language)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_qa_sqlite_question ON qa_pairs(question_text)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_qa_sqlite_lang ON qa_pairs(language)")
        self._sqlite.commit()

    def _init_postgres_schema(self):
        cur = self._pg.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS qa_pairs (
                qa_id SERIAL PRIMARY KEY,
                question_text TEXT NOT NULL,
                answer_text TEXT NOT NULL,
                language TEXT DEFAULT 'tw',
                usage_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(question_text, language)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_qa_pg_question ON qa_pairs(question_text)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_qa_pg_lang ON qa_pairs(language)")
        self._pg.commit()

    @staticmethod
    def _normalize(q: str) -> str:
        """Normalize for matching: lowercase, strip, remove trailing punctuation."""
        import re
        s = (q or "").strip().lower()
        s = re.sub(r"[.?!,;:]+$", "", s)
        s = re.sub(r"^\s+|\s+$", "", s)
        return s

    def find_qa_pair(self, question_text: str, language: str = "tw") -> Optional[Dict]:
        """
        Look up Q&A: PostgreSQL first, then SQLite.
        Returns first match. Updates usage_count/last_used in the backend that matched.
        """
        q = self._normalize(question_text or "")
        if not q:
            return None

        # 1. Try PostgreSQL
        if self._pg_available:
            try:
                with self._pg.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT qa_id, question_text, answer_text, language,
                               usage_count, last_used, created_at, updated_at
                        FROM qa_pairs
                        WHERE LOWER(TRIM(question_text)) = %s AND language = %s
                        LIMIT 1
                    """, (q, language))
                    row = cur.fetchone()
                    if row:
                        d = dict(row)
                        cur.execute("""
                            UPDATE qa_pairs
                            SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                            WHERE qa_id = %s
                        """, (d["qa_id"],))
                        self._pg.commit()
                        return d
                    # Fuzzy: fetch all, prefer longest (most specific) question first
                    cur.execute("""
                        SELECT qa_id, question_text, answer_text, language,
                               usage_count, last_used, created_at, updated_at
                        FROM qa_pairs WHERE language = %s
                    """, (language,))
                    pg_rows = cur.fetchall()
                    # Skip fuzzy when query is 1 word (e.g. "cultiflow") – avoid matching who-owns for everything
                    if len(q.split()) >= 2:
                        by_len = sorted(pg_rows, key=lambda r: len(self._normalize(r["question_text"] or "")), reverse=True)
                        for r in by_len:
                            stored = self._normalize(r["question_text"] or "")
                            if not stored or len(stored.split()) <= 1:
                                continue
                            if stored == q or stored in q or q in stored:
                                d = dict(r)
                                cur.execute("""
                                    UPDATE qa_pairs
                                    SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                                    WHERE qa_id = %s
                                """, (d["qa_id"],))
                                self._pg.commit()
                                return d
                    # Keyword fallback: "company" + "name" -> company-name answer
                    if "company" in q and "name" in q:
                        for r in pg_rows:
                            stored = self._normalize(r["question_text"] or "")
                            if "company" in stored and "name" in stored:
                                ans = (r["answer_text"] or "").lower()
                                if "cultiflow" in ans:
                                    d = dict(r)
                                    cur.execute("""
                                        UPDATE qa_pairs SET usage_count = usage_count + 1,
                                        last_used = CURRENT_TIMESTAMP WHERE qa_id = %s
                                    """, (d["qa_id"],))
                                    self._pg.commit()
                                    return d
                                break
            except Exception as e:
                print(f"WARNING: PostgreSQL find_qa_pair failed: {e}", flush=True)

        # 2. Try SQLite
        if self._sqlite_available:
            try:
                cur = self._sqlite.cursor()
                cur.execute("""
                    SELECT qa_id, question_text, answer_text, language,
                           usage_count, last_used, created_at, updated_at
                    FROM qa_pairs WHERE language = ?
                """, (language,))
                rows = cur.fetchall()
                for r in rows:
                    stored = self._normalize(r["question_text"] or "")
                    if not stored:
                        continue
                    if stored == q:
                        d = dict(r)
                        cur.execute("""
                            UPDATE qa_pairs
                            SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                            WHERE qa_id = ?
                        """, (d["qa_id"],))
                        self._sqlite.commit()
                        return d
                # Fuzzy: prefer longest (most specific) first; skip if query is 1 word only
                if len(q.split()) >= 2:
                    by_len = sorted(rows, key=lambda r: len(self._normalize(r["question_text"] or "")), reverse=True)
                    for r in by_len:
                        stored = self._normalize(r["question_text"] or "")
                        if not stored or len(stored.split()) <= 1:
                            continue
                        if stored in q or q in stored:
                            d = dict(r)
                            cur.execute("""
                                UPDATE qa_pairs
                                SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                                WHERE qa_id = ?
                            """, (d["qa_id"],))
                            self._sqlite.commit()
                            return d
                # Keyword fallback: "company" + "name" -> company-name answer
                if "company" in q and "name" in q:
                    for r in rows:
                        stored = self._normalize(r["question_text"] or "")
                        if "company" in stored and "name" in stored:
                            ans = (r["answer_text"] or "").lower()
                            if "cultiflow" in ans:
                                d = dict(r)
                                cur.execute("""
                                    UPDATE qa_pairs SET usage_count = usage_count + 1,
                                    last_used = CURRENT_TIMESTAMP WHERE qa_id = ?
                                """, (d["qa_id"],))
                                self._sqlite.commit()
                                return d
                            break
            except Exception as e:
                print(f"WARNING: SQLite find_qa_pair failed: {e}", flush=True)

        return None

    def add_qa_pair(self, question_text: str, answer_text: str, language: str = "tw") -> int:
        """Add or update Q&A in both PostgreSQL and SQLite. Returns qa_id from primary (PG if available, else SQLite)."""
        qn = (question_text or "").strip()
        an = (answer_text or "").strip()
        ql = qn.lower()
        qa_id: Optional[int] = None

        def _upsert_sqlite():
            cur = self._sqlite.cursor()
            cur.execute(
                "SELECT qa_id FROM qa_pairs WHERE LOWER(TRIM(question_text)) = ? AND language = ?",
                (ql, language),
            )
            ex = cur.fetchone()
            if ex:
                cur.execute(
                    "UPDATE qa_pairs SET answer_text = ?, updated_at = CURRENT_TIMESTAMP WHERE qa_id = ?",
                    (an, ex["qa_id"]),
                )
                self._sqlite.commit()
                return ex["qa_id"]
            cur.execute(
                "INSERT INTO qa_pairs (question_text, answer_text, language) VALUES (?, ?, ?)",
                (qn, an, language),
            )
            self._sqlite.commit()
            return cur.lastrowid

        def _upsert_pg():
            with self._pg.cursor() as cur:
                cur.execute(
                    "SELECT qa_id FROM qa_pairs WHERE LOWER(TRIM(question_text)) = %s AND language = %s",
                    (ql, language),
                )
                ex = cur.fetchone()
                if ex:
                    pk = ex[0] if isinstance(ex, (tuple, list)) else ex["qa_id"]
                    cur.execute(
                        "UPDATE qa_pairs SET answer_text = %s, updated_at = CURRENT_TIMESTAMP WHERE qa_id = %s",
                        (an, pk),
                    )
                    self._pg.commit()
                    return pk
                cur.execute(
                    "INSERT INTO qa_pairs (question_text, answer_text, language) VALUES (%s, %s, %s) RETURNING qa_id",
                    (qn, an, language),
                )
                (rid,) = cur.fetchone()
                self._pg.commit()
                return rid

        # Write to both; primary determines returned id
        if self._pg_available:
            try:
                qa_id = _upsert_pg()
            except Exception as e:
                print(f"WARNING: PostgreSQL add_qa_pair failed: {e}", flush=True)
        if self._sqlite_available:
            try:
                sid = _upsert_sqlite()
                if qa_id is None:
                    qa_id = sid
            except Exception as e:
                print(f"WARNING: SQLite add_qa_pair failed: {e}", flush=True)

        return qa_id or 0

    def get_qa_pair(self, qa_id: int) -> Optional[Dict]:
        """Get Q&A by id from PostgreSQL first, then SQLite."""
        if self._pg_available:
            try:
                with self._pg.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        "SELECT qa_id, question_text, answer_text, language, usage_count, last_used, created_at, updated_at FROM qa_pairs WHERE qa_id = %s",
                        (qa_id,),
                    )
                    row = cur.fetchone()
                    if row:
                        return dict(row)
            except Exception as e:
                print(f"WARNING: PostgreSQL get_qa_pair failed: {e}", flush=True)
        if self._sqlite_available:
            try:
                cur = self._sqlite.cursor()
                cur.execute(
                    "SELECT qa_id, question_text, answer_text, language, usage_count, last_used, created_at, updated_at FROM qa_pairs WHERE qa_id = ?",
                    (qa_id,),
                )
                row = cur.fetchone()
                if row:
                    return dict(row)
            except Exception as e:
                print(f"WARNING: SQLite get_qa_pair failed: {e}", flush=True)
        return None

    def get_all_qa_pairs(
        self,
        language: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """Fetch from PostgreSQL first; if empty and SQLite available, add SQLite results. Dedupe by (question_text, language)."""
        seen = set()
        out: List[Dict] = []

        def add_unique(row: Dict):
            k = ((row.get("question_text") or "").strip().lower(), row.get("language") or "tw")
            if k in seen:
                return
            seen.add(k)
            out.append(row)

        if self._pg_available:
            try:
                with self._pg.cursor(cursor_factory=RealDictCursor) as cur:
                    q = "SELECT * FROM qa_pairs"
                    params = []
                    if language:
                        q += " WHERE language = %s"
                        params.append(language)
                    q += " ORDER BY usage_count DESC, last_used DESC NULLS LAST"
                    if limit:
                        q += " LIMIT %s"
                        params.append(limit)
                    cur.execute(q, params)
                    for r in cur.fetchall():
                        add_unique(dict(r))
            except Exception as e:
                print(f"WARNING: PostgreSQL get_all_qa_pairs failed: {e}", flush=True)

        if self._sqlite_available:
            try:
                cur = self._sqlite.cursor()
                q = "SELECT * FROM qa_pairs"
                params = []
                if language:
                    q += " WHERE language = ?"
                    params.append(language)
                q += " ORDER BY usage_count DESC, last_used DESC"
                if limit:
                    q += " LIMIT ?"
                    params.append(limit)
                cur.execute(q, params)
                for r in cur.fetchall():
                    add_unique(dict(r))
            except Exception as e:
                print(f"WARNING: SQLite get_all_qa_pairs failed: {e}", flush=True)

        if limit and len(out) > limit:
            out = out[:limit]
        return out

    def delete_qa_pair(self, qa_id: int) -> bool:
        """Delete from both backends. Returns True if at least one deleted."""
        ok = False
        if self._pg_available:
            try:
                with self._pg.cursor() as cur:
                    cur.execute("DELETE FROM qa_pairs WHERE qa_id = %s", (qa_id,))
                    self._pg.commit()
                    ok = cur.rowcount > 0
            except Exception as e:
                print(f"WARNING: PostgreSQL delete_qa_pair failed: {e}", flush=True)
        if self._sqlite_available:
            try:
                cur = self._sqlite.cursor()
                cur.execute("DELETE FROM qa_pairs WHERE qa_id = ?", (qa_id,))
                self._sqlite.commit()
                ok = ok or cur.rowcount > 0
            except Exception as e:
                print(f"WARNING: SQLite delete_qa_pair failed: {e}", flush=True)
        return ok

    def close(self):
        if self._sqlite:
            try:
                self._sqlite.close()
            except Exception:
                pass
            self._sqlite = None
        if self._pg:
            try:
                self._pg.close()
            except Exception:
                pass
            self._pg = None


# Singleton for app use
_qa_store: Optional[QAStore] = None


def get_qa_store(
    sqlite_path: str = "voice_assistant.db",
    postgres_uri: Optional[str] = None,
) -> QAStore:
    global _qa_store
    if _qa_store is None:
        _qa_store = QAStore(sqlite_path=sqlite_path, postgres_uri=postgres_uri)
    return _qa_store
