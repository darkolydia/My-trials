#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q&A Management Utility
Add, update, delete, and view Q&A pairs in the database.

Store English-only Q&A. The voice assistant uses Twi STT -> translate to English
-> lookup -> translate answer to Twi -> Twi TTS, so callers hear Twi.
"""

import sys
import argparse
from pathlib import Path
from database import VoiceAssistantDB

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def add_qa(db, question, answer, language="tw"):
    """Add a Q&A pair"""
    qa_id = db.add_qa_pair(question, answer, language)
    print(f"✓ Added Q&A pair (ID: {qa_id})")
    print(f"  Question: {question}")
    print(f"  Answer: {answer}")
    print(f"  Language: {language}")


def update_qa(db, qa_id, question=None, answer=None):
    """Update a Q&A pair"""
    existing = db.get_qa_pair(qa_id)
    if not existing:
        print(f"✗ Q&A pair with ID {qa_id} not found.")
        return False
    
    new_question = question if question else existing['question_text']
    new_answer = answer if answer else existing['answer_text']
    
    db.add_qa_pair(new_question, new_answer, existing['language'])
    print(f"✓ Updated Q&A pair (ID: {qa_id})")
    print(f"  Question: {new_question}")
    print(f"  Answer: {new_answer}")
    return True


def delete_qa(db, qa_id):
    """Delete a Q&A pair"""
    if db.delete_qa_pair(qa_id):
        print(f"✓ Deleted Q&A pair (ID: {qa_id})")
        return True
    else:
        print(f"✗ Q&A pair with ID {qa_id} not found.")
        return False


def view_qa(db, qa_id):
    """View a specific Q&A pair"""
    qa = db.get_qa_pair(qa_id)
    if not qa:
        print(f"✗ Q&A pair with ID {qa_id} not found.")
        return
    
    print(f"\n{'='*60}")
    print(f"Q&A Pair ID: {qa['qa_id']}")
    print(f"{'='*60}")
    print(f"Question: {qa['question_text']}")
    print(f"Answer: {qa['answer_text']}")
    print(f"Language: {qa['language']}")
    print(f"Usage Count: {qa['usage_count']}")
    print(f"Last Used: {qa['last_used'] or 'Never'}")
    print(f"Created: {qa['created_at']}")
    print(f"Updated: {qa['updated_at']}")
    print(f"{'='*60}")


def search_qa(db, search_term, language=None):
    """Search for Q&A pairs"""
    all_pairs = db.get_all_qa_pairs(language=language)
    search_lower = search_term.lower()
    
    matches = []
    for qa in all_pairs:
        if (search_lower in qa['question_text'].lower() or 
            search_lower in qa['answer_text'].lower()):
            matches.append(qa)
    
    if not matches:
        print(f"No Q&A pairs found matching '{search_term}'")
        return
    
    print(f"\nFound {len(matches)} matching Q&A pair(s):")
    print(f"{'='*60}")
    for qa in matches:
        print(f"\n[ID: {qa['qa_id']}]")
        print(f"  Question: {qa['question_text']}")
        print(f"  Answer: {qa['answer_text']}")
        print(f"  Usage: {qa['usage_count']} times")


def main():
    parser = argparse.ArgumentParser(
        description="Manage Q&A pairs in the voice assistant database"
    )
    parser.add_argument(
        "--db",
        default="voice_assistant.db",
        help="Path to database file (default: voice_assistant.db)"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new Q&A pair')
    add_parser.add_argument('question', help='Question text (English)')
    add_parser.add_argument('answer', help='Answer text (English)')
    add_parser.add_argument('--language', default='en', help='Language code (default: en; use en for English-only store)')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update an existing Q&A pair')
    update_parser.add_argument('qa_id', type=int, help='Q&A pair ID')
    update_parser.add_argument('--question', help='New question text')
    update_parser.add_argument('--answer', help='New answer text')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a Q&A pair')
    delete_parser.add_argument('qa_id', type=int, help='Q&A pair ID')
    
    # View command
    view_parser = subparsers.add_parser('view', help='View a Q&A pair')
    view_parser.add_argument('qa_id', type=int, help='Q&A pair ID')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all Q&A pairs')
    list_parser.add_argument('--language', help='Filter by language code')
    list_parser.add_argument('--limit', type=int, default=50, help='Maximum number to show')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search Q&A pairs')
    search_parser.add_argument('term', help='Search term')
    search_parser.add_argument('--language', help='Filter by language code')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        db = VoiceAssistantDB(args.db)
        
        if args.command == 'add':
            add_qa(db, args.question, args.answer, args.language)
        elif args.command == 'update':
            update_qa(db, args.qa_id, args.question, args.answer)
        elif args.command == 'delete':
            delete_qa(db, args.qa_id)
        elif args.command == 'view':
            view_qa(db, args.qa_id)
        elif args.command == 'list':
            qa_pairs = db.get_all_qa_pairs(language=args.language, limit=args.limit)
            print(f"\n{'='*60}")
            print(f"Q&A PAIRS" + (f" (Language: {args.language})" if args.language else ""))
            print(f"{'='*60}")
            if not qa_pairs:
                print("No Q&A pairs found.")
            else:
                for qa in qa_pairs:
                    print(f"\n[ID: {qa['qa_id']}] Usage: {qa['usage_count']}")
                    print(f"  Q: {qa['question_text']}")
                    print(f"  A: {qa['answer_text']}")
            print(f"\n{'='*60}")
            print(f"Total: {len(qa_pairs)} Q&A pairs")
        elif args.command == 'search':
            search_qa(db, args.term, args.language)
        
        db.close()
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
