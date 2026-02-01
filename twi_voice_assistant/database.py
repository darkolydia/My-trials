#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Module for Voice Assistant
Handles SQLite database operations for call logging and conversation tracking
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class VoiceAssistantDB:
    """SQLite database handler for voice assistant system"""
    
    def __init__(self, db_path: str = "voice_assistant.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
        cursor = self.conn.cursor()
        
        # Create calls table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calls (
                call_id INTEGER PRIMARY KEY AUTOINCREMENT,
                caller_id TEXT,
                extension TEXT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT DEFAULT 'active',
                duration_seconds INTEGER,
                audio_file_path TEXT,
                response_file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create conversations table (questions and answers)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id INTEGER,
                question_text TEXT,
                answer_text TEXT,
                question_audio_path TEXT,
                answer_audio_path TEXT,
                stt_processing_time REAL,
                tts_processing_time REAL,
                total_processing_time REAL,
                language TEXT DEFAULT 'tw',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (call_id) REFERENCES calls(call_id) ON DELETE CASCADE
            )
        """)
        
        # Q&A pairs: handled by qa_store (PostgreSQL + SQLite dual backend)
        
        # Create statistics table for analytics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE DEFAULT CURRENT_DATE,
                total_calls INTEGER DEFAULT 0,
                total_conversations INTEGER DEFAULT 0,
                avg_processing_time REAL,
                successful_calls INTEGER DEFAULT 0,
                failed_calls INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date)
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_calls_start_time ON calls(start_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_calls_status ON calls(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_call_id ON conversations(call_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at)")
        
        self.conn.commit()
        
        # Q&A store (PostgreSQL + SQLite) for questions/answers; caller answers from DB
        self.qa_store = None
        try:
            from qa_store import get_qa_store
            self.qa_store = get_qa_store(
                sqlite_path=str(self.db_path),
                postgres_uri=os.getenv("POSTGRES_URI") or os.getenv("DATABASE_URL"),
            )
        except Exception as e:
            print(f"WARNING: Q&A store init failed: {e}", flush=True)
        print(f"Database initialized: {self.db_path}", flush=True)
    
    def create_call(self, caller_id: Optional[str] = None, 
                    extension: str = "1002",
                    audio_file_path: Optional[str] = None) -> int:
        """
        Create a new call record
        
        Args:
            caller_id: SIP caller ID (if available)
            extension: Extension number called
            audio_file_path: Path to recorded audio file
            
        Returns:
            call_id: ID of the created call record
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO calls (caller_id, extension, audio_file_path, status)
            VALUES (?, ?, ?, 'active')
        """, (caller_id, extension, audio_file_path))
        self.conn.commit()
        return cursor.lastrowid
    
    def update_call(self, call_id: int, 
                   end_time: Optional[datetime] = None,
                   status: str = "completed",
                   duration_seconds: Optional[int] = None,
                   response_file_path: Optional[str] = None):
        """
        Update call record with completion information
        
        Args:
            call_id: Call ID to update
            end_time: Call end timestamp
            status: Call status (completed, failed, etc.)
            duration_seconds: Call duration in seconds
            response_file_path: Path to response audio file
        """
        cursor = self.conn.cursor()
        
        update_fields = []
        values = []
        
        if end_time:
            update_fields.append("end_time = ?")
            values.append(end_time)
        
        if status:
            update_fields.append("status = ?")
            values.append(status)
        
        if duration_seconds is not None:
            update_fields.append("duration_seconds = ?")
            values.append(duration_seconds)
        
        if response_file_path:
            update_fields.append("response_file_path = ?")
            values.append(response_file_path)
        
        if update_fields:
            values.append(call_id)
            query = f"UPDATE calls SET {', '.join(update_fields)} WHERE call_id = ?"
            cursor.execute(query, values)
            self.conn.commit()
    
    def add_conversation(self, call_id: int,
                        question_text: str,
                        answer_text: str,
                        question_audio_path: Optional[str] = None,
                        answer_audio_path: Optional[str] = None,
                        stt_processing_time: Optional[float] = None,
                        tts_processing_time: Optional[float] = None,
                        total_processing_time: Optional[float] = None,
                        language: str = "tw") -> int:
        """
        Add a conversation record (question-answer pair)
        
        Args:
            call_id: Associated call ID
            question_text: Transcribed question text
            answer_text: Generated answer text
            question_audio_path: Path to question audio file
            answer_audio_path: Path to answer audio file
            stt_processing_time: Time taken for STT (seconds)
            tts_processing_time: Time taken for TTS (seconds)
            total_processing_time: Total processing time (seconds)
            language: Language code
            
        Returns:
            conversation_id: ID of the created conversation record
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO conversations (
                call_id, question_text, answer_text, question_audio_path,
                answer_audio_path, stt_processing_time, tts_processing_time,
                total_processing_time, language
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (call_id, question_text, answer_text, question_audio_path,
              answer_audio_path, stt_processing_time, tts_processing_time,
              total_processing_time, language))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_call(self, call_id: int) -> Optional[Dict]:
        """Get call record by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM calls WHERE call_id = ?", (call_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_call_conversations(self, call_id: int) -> List[Dict]:
        """Get all conversations for a call"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM conversations 
            WHERE call_id = ? 
            ORDER BY created_at ASC
        """, (call_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_calls(self, limit: int = 10) -> List[Dict]:
        """Get recent calls"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM calls 
            ORDER BY start_time DESC 
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def find_qa_pair(self, question_text: str, language: str = "tw") -> Optional[Dict]:
        """
        Find a Q&A pair by question text (PostgreSQL first, then SQLite).
        """
        if not self.qa_store:
            return None
        return self.qa_store.find_qa_pair(question_text, language)
    
    def add_qa_pair(self, question_text: str, answer_text: str, 
                    language: str = "tw") -> int:
        """Add or update a Q&A pair in both PostgreSQL and SQLite."""
        if not self.qa_store:
            return 0
        return self.qa_store.add_qa_pair(question_text, answer_text, language)
    
    def get_qa_pair(self, qa_id: int) -> Optional[Dict]:
        """Get Q&A pair by ID from PostgreSQL or SQLite."""
        if not self.qa_store:
            return None
        return self.qa_store.get_qa_pair(qa_id)
    
    def get_all_qa_pairs(self, language: Optional[str] = None, 
                        limit: Optional[int] = None) -> List[Dict]:
        """Get all Q&A pairs from PostgreSQL + SQLite (merged, deduped)."""
        if not self.qa_store:
            return []
        return self.qa_store.get_all_qa_pairs(language=language, limit=limit)
    
    def delete_qa_pair(self, qa_id: int) -> bool:
        """Delete a Q&A pair from both PostgreSQL and SQLite."""
        if not self.qa_store:
            return False
        return self.qa_store.delete_qa_pair(qa_id)
    
    def get_statistics(self, date: Optional[str] = None) -> Dict:
        """
        Get statistics for a specific date or today
        
        Args:
            date: Date in YYYY-MM-DD format (default: today)
            
        Returns:
            Dictionary with statistics
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        cursor = self.conn.cursor()
        
        # Get call statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_calls,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_calls,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_calls,
                AVG(duration_seconds) as avg_duration
            FROM calls
            WHERE DATE(start_time) = ?
        """, (date,))
        
        call_stats = dict(cursor.fetchone() or {})
        
        # Get conversation statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_conversations,
                AVG(total_processing_time) as avg_processing_time,
                AVG(stt_processing_time) as avg_stt_time,
                AVG(tts_processing_time) as avg_tts_time
            FROM conversations
            WHERE DATE(created_at) = ?
        """, (date,))
        
        conv_stats = dict(cursor.fetchone() or {})
        
        return {
            "date": date,
            "calls": call_stats,
            "conversations": conv_stats
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Global database instance (can be initialized per call)
_db_instance = None


def get_db(db_path: str = "voice_assistant.db") -> VoiceAssistantDB:
    """
    Get or create database instance
    
    Args:
        db_path: Path to database file
        
    Returns:
        VoiceAssistantDB instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = VoiceAssistantDB(db_path)
    return _db_instance


if __name__ == "__main__":
    # Test database initialization
    db = VoiceAssistantDB("test_voice_assistant.db")
    
    # Test creating a call
    call_id = db.create_call(caller_id="1000", extension="1002", 
                             audio_file_path="test.wav")
    print(f"Created call with ID: {call_id}")
    
    # Test adding conversation
    conv_id = db.add_conversation(
        call_id=call_id,
        question_text="wo ho te sen",
        answer_text="Me ho ye. Meda wo ase.",
        stt_processing_time=3.5,
        tts_processing_time=2.8,
        total_processing_time=6.3
    )
    print(f"Created conversation with ID: {conv_id}")
    
    # Test updating call
    db.update_call(call_id, status="completed", duration_seconds=15)
    
    # Test retrieving call
    call = db.get_call(call_id)
    print(f"Retrieved call: {call}")
    
    # Test retrieving conversations
    conversations = db.get_call_conversations(call_id)
    print(f"Retrieved {len(conversations)} conversations")
    
    # Test statistics
    stats = db.get_statistics()
    print(f"Statistics: {stats}")
    
    db.close()
    print("Database test completed successfully!")
