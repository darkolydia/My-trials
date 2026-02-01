#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized Voice Assistant - Faster processing with caching
"""

import os
import sys
from pathlib import Path
import json

# Add the current directory to path to import voice_assistant
sys.path.insert(0, str(Path(__file__).parent))

from voice_assistant import process_voice_query

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Optimized Voice Assistant")
    parser.add_argument("audio_file", help="Path to recorded audio file")
    parser.add_argument("-o", "--output", help="Output audio file", default=None)
    
    args = parser.parse_args()
    
    # Process with minimal output for faster execution
    result = process_voice_query(args.audio_file, args.output)
    
    if result:
        # Just print the result path for FreeSWITCH to use
        print(result)
        sys.exit(0)
    else:
        sys.exit(1)
