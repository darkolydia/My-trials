#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Q&A matching functionality.
"""

from voice_assistant import find_answer

# Test questions
test_questions = [
    "hello",
    "hi there",
    "what is your name",
    "who are you",
    "where are you located",
    "what is your address",
    "help me",
    "how can you help",
    "what can you do",
    "good morning",
    "good afternoon",
    "contact information",
    "phone number",
    "random question that doesn't match anything",
]

print("=" * 70)
print("TESTING Q&A MATCHING")
print("=" * 70)

for question in test_questions:
    print(f"\nQuestion: '{question}'")
    answer = find_answer(question)
    print(f"Answer: {answer}")
    print("-" * 70)

print("\n" + "=" * 70)
print("Testing complete!")
print("=" * 70)
