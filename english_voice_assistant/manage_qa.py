#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple script to view and manage Q&A pairs in the English voice assistant.
"""

import sys
from pathlib import Path

# Import Q&A pairs from voice_assistant
sys.path.insert(0, str(Path(__file__).parent))
from voice_assistant import QA_PAIRS, QA_KEYWORDS


def list_all_qa():
    """List all Q&A pairs"""
    print("=" * 60)
    print("Q&A PAIRS (Exact/Partial Match)")
    print("=" * 60)
    for i, (question, answer) in enumerate(QA_PAIRS.items(), 1):
        if question != "default":
            print(f"\n{i}. Question: {question}")
            print(f"   Answer: {answer}")
    
    print("\n" + "=" * 60)
    print("KEYWORD-BASED Q&A")
    print("=" * 60)
    for i, (keyword, answer) in enumerate(QA_KEYWORDS.items(), 1):
        print(f"\n{i}. Keyword: {keyword}")
        print(f"   Answer: {answer}")
    
    print("\n" + "=" * 60)
    print(f"Default fallback: {QA_PAIRS.get('default', 'Not set')}")
    print("=" * 60)


def test_question(question):
    """Test how a question would be matched"""
    from voice_assistant import find_answer
    
    print(f"\nTesting question: '{question}'")
    print("-" * 60)
    answer = find_answer(question)
    print(f"Answer: {answer}")
    print("-" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Manage Q&A pairs for English Voice Assistant"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all Q&A pairs"
    )
    parser.add_argument(
        "--test",
        help="Test how a question would be matched"
    )
    
    args = parser.parse_args()
    
    if args.test:
        test_question(args.test)
    else:
        list_all_qa()
