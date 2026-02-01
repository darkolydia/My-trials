#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Viewer Utility
View call logs, conversations, and statistics from the voice assistant database
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from database import VoiceAssistantDB

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def print_call(call):
    """Print formatted call information"""
    print(f"\n{'='*60}")
    print(f"Call ID: {call['call_id']}")
    print(f"Caller ID: {call['caller_id'] or 'N/A'}")
    print(f"Extension: {call['extension']}")
    print(f"Status: {call['status']}")
    print(f"Start Time: {call['start_time']}")
    print(f"End Time: {call['end_time'] or 'N/A'}")
    print(f"Duration: {call['duration_seconds'] or 'N/A'} seconds")
    print(f"Audio File: {call['audio_file_path'] or 'N/A'}")
    print(f"Response File: {call['response_file_path'] or 'N/A'}")
    print(f"{'='*60}")


def print_conversation(conv):
    """Print formatted conversation information"""
    print(f"\n  Conversation ID: {conv['conversation_id']}")
    print(f"  Question: {conv['question_text']}")
    print(f"  Answer: {conv['answer_text']}")
    print(f"  STT Time: {conv['stt_processing_time'] or 'N/A'}s")
    print(f"  TTS Time: {conv['tts_processing_time'] or 'N/A'}s")
    print(f"  Total Time: {conv['total_processing_time'] or 'N/A'}s")
    print(f"  Created: {conv['created_at']}")


def list_recent_calls(db, limit=10):
    """List recent calls"""
    print(f"\n{'='*60}")
    print(f"RECENT CALLS (Last {limit})")
    print(f"{'='*60}")
    
    calls = db.get_recent_calls(limit)
    if not calls:
        print("No calls found.")
        return
    
    for call in calls:
        print_call(call)
        
        # Get conversations for this call
        conversations = db.get_call_conversations(call['call_id'])
        if conversations:
            print(f"\n  Conversations ({len(conversations)}):")
            for conv in conversations:
                print_conversation(conv)


def view_call(db, call_id):
    """View specific call details"""
    call = db.get_call(call_id)
    if not call:
        print(f"Call ID {call_id} not found.")
        return
    
    print_call(call)
    
    # Get conversations
    conversations = db.get_call_conversations(call_id)
    if conversations:
        print(f"\nConversations ({len(conversations)}):")
        for conv in conversations:
            print_conversation(conv)
    else:
        print("\nNo conversations found for this call.")


def show_statistics(db, date=None):
    """Show statistics for a date"""
    stats = db.get_statistics(date)
    
    print(f"\n{'='*60}")
    print(f"STATISTICS - {stats['date']}")
    print(f"{'='*60}")
    
    print("\nCALL STATISTICS:")
    call_stats = stats['calls']
    print(f"  Total Calls: {call_stats.get('total_calls', 0) or 0}")
    print(f"  Successful: {call_stats.get('successful_calls', 0) or 0}")
    print(f"  Failed: {call_stats.get('failed_calls', 0) or 0}")
    avg_duration = call_stats.get('avg_duration')
    if avg_duration:
        print(f"  Avg Duration: {avg_duration:.2f} seconds")
    
    print("\nCONVERSATION STATISTICS:")
    conv_stats = stats['conversations']
    print(f"  Total Conversations: {conv_stats.get('total_conversations', 0) or 0}")
    avg_processing = conv_stats.get('avg_processing_time')
    if avg_processing:
        print(f"  Avg Processing Time: {avg_processing:.2f} seconds")
    avg_stt = conv_stats.get('avg_stt_time')
    if avg_stt:
        print(f"  Avg STT Time: {avg_stt:.2f} seconds")
    avg_tts = conv_stats.get('avg_tts_time')
    if avg_tts:
        print(f"  Avg TTS Time: {avg_tts:.2f} seconds")
    
    print(f"\n{'='*60}")


def list_qa_pairs(db, language=None, limit=20):
    """List Q&A pairs"""
    print(f"\n{'='*60}")
    print(f"Q&A PAIRS" + (f" (Language: {language})" if language else ""))
    print(f"{'='*60}")
    
    qa_pairs = db.get_all_qa_pairs(language=language, limit=limit)
    if not qa_pairs:
        print("No Q&A pairs found.")
        return
    
    for i, qa in enumerate(qa_pairs, 1):
        print(f"\n[{i}] Q&A ID: {qa['qa_id']}")
        print(f"    Question: {qa['question_text']}")
        print(f"    Answer: {qa['answer_text']}")
        print(f"    Language: {qa['language']}")
        print(f"    Usage Count: {qa['usage_count']}")
        print(f"    Last Used: {qa['last_used'] or 'Never'}")
        print(f"    Created: {qa['created_at']}")
    
    print(f"\n{'='*60}")
    print(f"Total: {len(qa_pairs)} Q&A pairs")


def main():
    parser = argparse.ArgumentParser(
        description="View voice assistant database records and statistics"
    )
    parser.add_argument(
        "--db",
        default="voice_assistant.db",
        help="Path to database file (default: voice_assistant.db)"
    )
    parser.add_argument(
        "--list",
        type=int,
        metavar="N",
        help="List recent N calls (default: 10)"
    )
    parser.add_argument(
        "--call",
        type=int,
        metavar="ID",
        help="View specific call by ID"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics for today"
    )
    parser.add_argument(
        "--date",
        help="Date for statistics (YYYY-MM-DD format)"
    )
    parser.add_argument(
        "--qa",
        action="store_true",
        help="List Q&A pairs"
    )
    parser.add_argument(
        "--language",
        help="Filter by language code (e.g., 'tw')"
    )
    parser.add_argument(
        "--qa-limit",
        type=int,
        default=20,
        help="Limit number of Q&A pairs to show (default: 20)"
    )
    
    args = parser.parse_args()
    
    # Default action: list recent calls
    if not any([args.list, args.call, args.stats, args.qa]):
        args.list = 10
    
    try:
        db = VoiceAssistantDB(args.db)
        
        if args.call:
            view_call(db, args.call)
        elif args.stats:
            show_statistics(db, args.date)
        elif args.qa:
            list_qa_pairs(db, language=args.language, limit=args.qa_limit)
        elif args.list:
            list_recent_calls(db, args.list)
        
        db.close()
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
