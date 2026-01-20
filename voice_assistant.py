#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voice Assistant - Interactive Q&A System
Handles: Speech-to-Text -> Question Processing -> Text-to-Speech
"""

import os
import sys
import json
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Manual .env parsing
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

try:
    from ghana_nlp import GhanaNLP
except ImportError:
    print("ERROR: ghana-nlp package not installed.")
    print("Install it with: pip install ghana-nlp")
    sys.exit(1)

try:
    import soundfile as sf
except ImportError:
    print("WARNING: soundfile not installed. Audio conversion may fail.")
    soundfile = None


def get_api_key():
    """Get Ghana NLP API key from environment"""
    api_key = os.getenv("GHANANLP_API_KEY") or os.getenv("GHANA_NLP_API_KEY")
    if not api_key:
        print("ERROR: Ghana NLP API key required!")
        print("Set it in .env file: GHANANLP_API_KEY=your_key")
        sys.exit(1)
    return api_key


def speech_to_text(audio_file, api_key, lang="tw"):
    """
    Convert speech audio to text using Ghana NLP ASR
    
    Args:
        audio_file: Path to audio file (WAV format)
        api_key: Ghana NLP API key
        lang: Language code (tw for Twi)
    
    Returns:
        Transcribed text string
    """
    try:
        nlp = GhanaNLP(api_key=api_key)
        
        # Use Ghana NLP STT (Speech-to-Text)
        # The stt method takes audio_file_path and language code
        if hasattr(nlp, 'stt'):
            try:
                # STT takes file path, not audio data
                # Convert Windows path to forward slashes if needed
                audio_path = str(audio_file).replace('\\', '/')
                print(f"Calling STT with file: {audio_path}", flush=True)
                result = nlp.stt(audio_path, language=lang)
                print(f"STT result type: {type(result)}", flush=True)
                print(f"STT result: {result}", flush=True)
                # Handle different return types
                if isinstance(result, str):
                    return result
                elif isinstance(result, dict):
                    return result.get('text', result.get('transcription', ''))
                else:
                    return str(result)
            except Exception as e:
                print(f"ERROR: STT call failed: {e}", flush=True)
                import traceback
                traceback.print_exc()
                return None
        else:
            print("ERROR: Ghana NLP STT not available", flush=True)
            return None
            
    except Exception as e:
        print(f"ERROR: Speech-to-text failed: {e}")
        return None


def process_question(question_text, lang="tw"):
    """
    Process the question and generate an answer
    
    For now, using simple keyword matching.
    Can be extended to use LLM (OpenAI, Ollama, etc.)
    
    Args:
        question_text: The user's question in Twi
        lang: Language code
    
    Returns:
        Answer text in Twi
    """
    question_lower = question_text.lower()
    
    # Simple keyword-based responses (in Twi)
    responses = {
        "wo ho te sɛn": "Me ho ye. Meda wo ase sɛ wobu me. Wo ho te sɛn?",
        "wo ho te sen": "Me ho ye. Meda wo ase sɛ wobu me. Wo ho te sɛn?",
        "ɛte sɛn": "Ɛyɛ. Me ho ye. Ɛte sɛn wo nso?",
        "akwaaba": "Meda wo ase. Yɛma wo akwaaba!",
        "meda wo ase": "Mepa wo kyɛw. Ɛyɛ me anigyeɛ sɛ meka wo ho.",
        "me din": "Me din ne Cultiflow Voice Assistant. Me bɛboa wo sɛn?",
        "wo din": "Me din ne Cultiflow Voice Assistant. Me bɛboa wo sɛn?",
        "help": "Mepɛ sɛ meboa wo. Ka me sɛn na ɛsɛ sɛ meyɛ ma wo.",
        "boa me": "Mepɛ sɛ meboa wo. Ka me sɛn na ɛsɛ sɛ meyɛ ma wo.",
    }
    
    # Check for keywords
    for keyword, response in responses.items():
        if keyword in question_lower:
            return response
    
    # Default response if no keyword matches
    return "Meda wo ase sɛ wobu me. Mepɛ sɛ meboa wo, nanso me nte asɛm no yi yiye. San ka bio, anaa ka me sɛn na ɛsɛ sɛ meyɛ ma wo."


def text_to_speech(text, api_key, output_file, lang="tw"):
    """
    Convert text to speech using Ghana NLP TTS
    
    Args:
        text: Text to convert to speech
        api_key: Ghana NLP API key
        output_file: Path to save the audio file
        lang: Language code (tw for Twi)
    
    Returns:
        Path to generated audio file, or None if failed
    """
    try:
        nlp = GhanaNLP(api_key=api_key)
        
        # Generate TTS
        audio_binary = nlp.tts(text, lang=lang)
        
        # Save to temporary file
        temp_file = Path(output_file).parent / f"temp_{Path(output_file).name}"
        with open(temp_file, "wb") as f:
            f.write(audio_binary)
        
        # Convert to FreeSWITCH-compatible format (PCM 16-bit, 16kHz mono)
        try:
            import soundfile as sf
            try:
                data, sr = sf.read(str(temp_file))
                sf.write(str(output_file), data, 16000, subtype='PCM_16')
                temp_file.unlink()
                print(f"  ✓ Converted audio to FreeSWITCH-compatible format", flush=True)
                return str(output_file)
            except Exception as e:
                print(f"WARNING: Audio conversion failed: {e}", flush=True)
                # Use original file
                temp_file.rename(output_file)
                return str(output_file)
        except ImportError:
            # No soundfile available, use as-is
            print(f"WARNING: soundfile not available, using original format", flush=True)
            temp_file.rename(output_file)
            return str(output_file)
            
    except Exception as e:
        print(f"ERROR: Text-to-speech failed: {e}")
        return None


def process_voice_query(audio_file, output_file=None):
    """
    Main function: Process a voice query and generate response audio
    
    Flow:
    1. Speech-to-Text: Convert audio to text
    2. Process Question: Generate answer
    3. Text-to-Speech: Convert answer to audio
    
    Args:
        audio_file: Path to recorded audio file
        output_file: Path to save response audio (optional)
    
    Returns:
        Path to response audio file, or None if failed
    """
    if output_file is None:
        output_file = Path(audio_file).parent / "response.wav"
    else:
        output_file = Path(output_file)
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    api_key = get_api_key()
    
    print(f"Processing voice query from: {audio_file}", flush=True)
    
    # Step 1: Speech-to-Text
    print("Step 1: Converting speech to text...", flush=True)
    question_text = speech_to_text(audio_file, api_key, lang="tw")
    
    if not question_text:
        print("ERROR: Could not transcribe speech", flush=True)
        # Return a default error response audio
        error_text = "Mepa wo kyɛw, me nte asɛm no yi yiye. San ka bio."
        text_to_speech(error_text, api_key, str(output_file), lang="tw")
        return str(output_file)
    
    print(f"Transcribed question: {question_text}", flush=True)
    
    # Step 2: Process question and generate answer
    print("Step 2: Processing question...", flush=True)
    answer_text = process_question(question_text, lang="tw")
    print(f"Generated answer: {answer_text}", flush=True)
    
    # Step 3: Text-to-Speech
    print("Step 3: Converting answer to speech...", flush=True)
    response_file = text_to_speech(answer_text, api_key, str(output_file), lang="tw")
    
    if not response_file:
        print("ERROR: Could not generate speech", flush=True)
        return None
    
    print(f"Response audio saved to: {response_file}", flush=True)
    return response_file


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Voice Assistant - Process voice queries and generate responses"
    )
    parser.add_argument(
        "audio_file",
        help="Path to recorded audio file (WAV format)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output audio file path (default: response.wav in same directory)",
        default=None
    )
    
    args = parser.parse_args()
    
    if not Path(args.audio_file).exists():
        print(f"ERROR: Audio file not found: {args.audio_file}")
        sys.exit(1)
    
    result = process_voice_query(args.audio_file, args.output)
    
    if result:
        print(f"\n✓ Success! Response audio: {result}")
        sys.exit(0)
    else:
        print("\n✗ Failed to process voice query")
        sys.exit(1)
