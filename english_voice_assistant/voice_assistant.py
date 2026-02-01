#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
English Voice Assistant - Simple Q&A System
Handles: Speech-to-Text (English) -> Question Matching -> Text-to-Speech (English)

Flow: User speaks English -> STT(English) -> lookup Q&A pairs -> TTS(English).
No database, no translation - simple hardcoded Q&A pairs.
"""

import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime

# Project root = directory containing this script
PROJECT_ROOT = Path(__file__).resolve().parent
# When TTS fails, copy this to response.wav so we don't replay the previous answer
FALLBACK_WAV = PROJECT_ROOT / "sounds" / "custom" / "please_wait.wav"
# Fixed recordings dir for logs
RECORDINGS_DIR = Path(r"C:\Users\User\Desktop\Recordings")

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load .env from project root
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
        except Exception:
            pass

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


# Hardcoded Q&A pairs - English questions and answers
QA_PAIRS = {
    # Greetings
    "hello": "Hello! How can I help you today?",
    "hi": "Hi there! What can I do for you?",
    "good morning": "Good morning! How may I assist you?",
    "good afternoon": "Good afternoon! How can I help you?",
    "good evening": "Good evening! What do you need?",
    
    # Common questions
    "what is your name": "I am a voice assistant. How can I help you?",
    "who are you": "I am a voice assistant designed to answer your questions.",
    "what can you do": "I can answer questions and help you with information. What would you like to know?",
    
    # Location/Company questions
    "where are you located": "I am a virtual assistant, so I don't have a physical location.",
    "where is the office": "Please contact our main office for location information.",
    "what is your address": "For address information, please contact our main office.",
    
    # Help/Support
    "how can you help me": "I can answer questions and provide information. What would you like to know?",
    "what do you do": "I answer questions and provide information. Ask me anything!",
    "help": "I'm here to help! What do you need assistance with?",
    
    # Default fallback
    "default": "I'm sorry, I didn't understand that clearly. Could you please repeat your question?"
}

# Additional variations - these will be matched using keyword matching
QA_KEYWORDS = {
    "name": "I am a voice assistant. How can I help you?",
    "location": "For location information, please contact our main office.",
    "address": "For address information, please contact our main office.",
    "help": "I'm here to help! What do you need assistance with?",
    "contact": "For contact information, please reach out to our main office.",
    "phone": "For phone number information, please contact our main office.",
    "email": "For email information, please contact our main office.",
}


def speech_to_text(audio_file, api_key, lang="en"):
    """
    Convert speech audio to text using Ghana NLP ASR
    
    Args:
        audio_file: Path to audio file (WAV format)
        api_key: Ghana NLP API key
        lang: Language code (en for English)
    
    Returns:
        Tuple of (transcribed text string, processing time in seconds)
    """
    start_time = time.time()
    try:
        nlp = GhanaNLP(api_key=api_key)
        
        if hasattr(nlp, 'stt'):
            try:
                audio_path = str(audio_file).replace('\\', '/')
                print(f"Calling STT with file: {audio_path}", flush=True)
                result = nlp.stt(audio_path, language=lang)
                print(f"STT result type: {type(result)}", flush=True)
                print(f"STT result: {result}", flush=True)
                processing_time = time.time() - start_time
                if isinstance(result, str):
                    return result, processing_time
                elif isinstance(result, dict):
                    if result.get("message"):
                        return None, processing_time
                    text = result.get("text") or result.get("transcription") or ""
                    return (text.strip() or None), processing_time
                else:
                    return str(result), processing_time
            except Exception as e:
                print(f"ERROR: STT call failed: {e}", flush=True)
                import traceback
                traceback.print_exc()
                return None, time.time() - start_time
        else:
            print("ERROR: Ghana NLP STT not available", flush=True)
            return None, time.time() - start_time
            
    except Exception as e:
        print(f"ERROR: Speech-to-text failed: {e}")
        return None, time.time() - start_time


def find_answer(question_text):
    """
    Find answer for a question using hardcoded Q&A pairs.
    First tries exact match, then keyword matching.
    
    Args:
        question_text: The question text (English)
    
    Returns:
        Answer text or default message
    """
    if not question_text:
        return QA_PAIRS["default"]
    
    q = question_text.strip().lower()
    print(f"[Q&A] question: {q!r}", flush=True)
    
    # Try exact match first
    if q in QA_PAIRS:
        print(f"[Q&A] exact match found", flush=True)
        return QA_PAIRS[q]
    
    # Try partial match (question contains key phrase)
    for key, answer in QA_PAIRS.items():
        if key != "default" and key in q:
            print(f"[Q&A] partial match: '{key}'", flush=True)
            return answer
    
    # Try keyword matching
    for keyword, answer in QA_KEYWORDS.items():
        if keyword in q:
            print(f"[Q&A] keyword match: '{keyword}'", flush=True)
            return answer
    
    print("[Q&A] no match, using default", flush=True)
    return QA_PAIRS["default"]


def _convert_to_wav(temp_path: Path, out_path: Path) -> bool:
    """Convert temp audio (WAV from Ghana TTS) to 16kHz 16-bit mono. Overwrites out_path."""
    out_path = Path(out_path)
    if out_path.exists():
        try:
            out_path.unlink()
        except Exception:
            pass
    # 1. soundfile (Ghana TTS returns WAV)
    try:
        import soundfile as sf
        import numpy as np
        data, sr = sf.read(str(temp_path), dtype="float64", always_2d=False)
        if data.ndim > 1:
            data = data.mean(axis=1)
        n = int(len(data) * 16000 / sr)
        x = np.linspace(0, len(data) - 1, n)
        data = np.interp(x, np.arange(len(data)), data).astype(np.float32)
        sf.write(str(out_path), data, 16000, subtype="PCM_16")
        return True
    except Exception as e:
        print(f"  DEBUG: soundfile conversion failed: {e}", flush=True)
        pass
    # 2. ffmpeg (auto-detect)
    try:
        import subprocess
        subprocess.run([
            "ffmpeg", "-i", str(temp_path),
            "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "-y", str(out_path)
        ], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    # 3. pydub (for MP3 from gTTS)
    for fmt in ("wav", "mp3"):
        try:
            from pydub import AudioSegment
            seg = AudioSegment.from_file(str(temp_path), format=fmt)
            seg = seg.set_frame_rate(16000).set_channels(1).set_sample_width(2)
            seg.export(str(out_path), format="wav")
            return True
        except Exception as e:
            print(f"  DEBUG: pydub conversion failed ({fmt}): {e}", flush=True)
            pass
    return False


def text_to_speech(text, api_key, output_file, lang="en"):
    """
    Text-to-Speech -> WAV. Converts to 16kHz 16-bit mono for FreeSWITCH.
    For English: Uses gTTS (Google Text-to-Speech) since Ghana NLP doesn't support English TTS.
    """
    start_time = time.time()
    out = Path(output_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    
    # For English, use gTTS (Google Text-to-Speech) since Ghana NLP doesn't support English
    if lang == "en":
        try:
            from gtts import gTTS
            import io
            temp_mp3 = out.parent / f"temp_tts_{out.stem}.mp3"
            
            # Generate speech using gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(str(temp_mp3))
            
            # Convert MP3 to WAV (16kHz, 16-bit, mono)
            if _convert_to_wav(temp_mp3, out):
                try:
                    temp_mp3.unlink()
                except Exception:
                    pass
                print(f"  ✓ TTS (gTTS) -> FreeSWITCH WAV", flush=True)
                return str(out), time.time() - start_time
            else:
                try:
                    temp_mp3.unlink()
                except Exception:
                    pass
                print(f"  ⚠ TTS conversion failed. Install ffmpeg or pydub.", flush=True)
                return None, time.time() - start_time
        except ImportError:
            print(f"ERROR: gTTS not installed. Install with: pip install gtts", flush=True)
            return None, time.time() - start_time
        except Exception as e:
            print(f"ERROR: gTTS failed: {e}", flush=True)
            return None, time.time() - start_time
    
    # For other languages (Twi, etc.), use Ghana NLP
    try:
        nlp = GhanaNLP(api_key=api_key)
        raw = nlp.tts(text, lang=lang)
        if isinstance(raw, dict):
            print(f"ERROR: TTS API error: {raw.get('message', raw)}", flush=True)
            return None, time.time() - start_time
        temp = out.parent / f"temp_tts_{out.stem}.wav"
        with open(temp, "wb") as f:
            f.write(raw)
        if _convert_to_wav(temp, out):
            try:
                temp.unlink()
            except Exception:
                pass
            print(f"  ✓ TTS (Ghana NLP) -> FreeSWITCH WAV", flush=True)
            return str(out), time.time() - start_time
        try:
            temp.unlink()
        except Exception:
            pass
        print(f"  ⚠ TTS conversion failed. Install ffmpeg or pydub.", flush=True)
        return None, time.time() - start_time
    except Exception as e:
        print(f"ERROR: Text-to-speech failed: {e}", flush=True)
        return None, time.time() - start_time


def process_voice_query(audio_file, output_file=None):
    """
    Main function: Process a voice query and generate response audio
    
    Flow:
    1. Speech-to-Text: Convert audio to text (English)
    2. Find Answer: Match question to hardcoded Q&A pairs
    3. Text-to-Speech: Convert answer to audio (English)
    
    Args:
        audio_file: Path to recorded audio file
        output_file: Path to save response audio (optional)
    
    Returns:
        Path to response audio file, or None if failed
    """
    total_start_time = time.time()
    
    if output_file is None:
        output_file = Path(audio_file).parent / "response.wav"
    else:
        output_file = Path(output_file)
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Logs: always use fixed RECORDINGS_DIR
    rec = RECORDINGS_DIR
    log_path = rec / "last_call_log.txt"
    live_log_path = rec / "live_log.txt"
    last_q_path = rec / "last_question.txt"

    def _write_log(*lines: str) -> None:
        try:
            rec.mkdir(parents=True, exist_ok=True)
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            print(f"Wrote {log_path}", flush=True)
        except Exception as e:
            print(f"WARNING: Could not write last_call_log: {e}", flush=True)

    def _append_live(*lines: str) -> None:
        try:
            rec.mkdir(parents=True, exist_ok=True)
            with open(live_log_path, "a", encoding="utf-8") as f:
                for line in lines:
                    f.write(line + "\n")
        except Exception:
            pass

    def _write_last_question(q: str, ans: str) -> None:
        """Overwrite last_question.txt so you can open it in Notepad after each call."""
        try:
            rec.mkdir(parents=True, exist_ok=True)
            with open(last_q_path, "w", encoding="utf-8") as f:
                f.write(f"question_en: {q}\n")
                f.write(f"answer_en: {ans}\n")
            print(f"Wrote {last_q_path}", flush=True)
        except Exception as e:
            print(f"WARNING: Could not write last_question: {e}", flush=True)

    _write_log(
        f"timestamp={datetime.now().isoformat()}",
        "status=started",
        f"audio_file={audio_file}",
        f"output_file={output_file}",
    )
    _write_last_question("(starting...)", "")
    
    # Overwrite response.wav immediately so we never play stale audio
    if FALLBACK_WAV.exists():
        try:
            shutil.copy2(FALLBACK_WAV, output_file)
            print("Cleared response.wav with fallback (will overwrite with real TTS)", flush=True)
        except Exception as e:
            print(f"WARNING: Could not clear response.wav: {e}", flush=True)
    
    api_key = get_api_key()
    
    print(f"Processing voice query from: {audio_file}", flush=True)
    
    # Step 1: Speech-to-Text (English)
    print("Step 1: Converting speech to text (English)...", flush=True)
    transcript, stt_time = speech_to_text(audio_file, api_key, lang="en")
    
    if not transcript:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        block = [
            "",
            f">>> {ts}",
            "=" * 60,
            "  YOUR QUESTION (transcribed)",
            "=" * 60,
            "  [Could not transcribe - STT failed]",
            "=" * 60,
            "",
        ]
        for line in block:
            print(line, flush=True)
        _append_live(*block)
        _write_last_question("[STT_FAILED]", "[STT_FAILED]")
        print("ERROR: Could not transcribe speech", flush=True)
        _write_log(
            f"timestamp={datetime.now().isoformat()}",
            "status=stt_failed",
            "transcript=None",
            "question_en=[STT_FAILED]",
            "answer_en=[STT_FAILED]",
            f"output_file={output_file}",
        )
        error_text = "I'm sorry, I couldn't understand that. Please try again."
        response_file, tts_time = text_to_speech(error_text, api_key, str(output_file), lang="en")
        if not response_file and FALLBACK_WAV.exists():
            shutil.copy2(FALLBACK_WAV, output_file)
            response_file = str(output_file)
            print("  ✓ Used fallback WAV (TTS failed)", flush=True)
        return str(response_file) if response_file else None
    
    # Step 2: Find answer from hardcoded Q&A pairs
    question_text = str(transcript or "").strip()
    
    # Log your question
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    block = [
        "",
        f">>> {ts}",
        "=" * 60,
        "  YOUR QUESTION (transcribed)",
        "=" * 60,
        f"  English: {question_text}",
        "=" * 60,
        "",
    ]
    for line in block:
        print(line, flush=True)
    _append_live(*block)

    print("Step 2: Finding answer from Q&A pairs...", flush=True)
    answer_text = find_answer(question_text)
    print(f"Generated answer (en): {answer_text}", flush=True)

    _write_log(
        f"timestamp={datetime.now().isoformat()}",
        "status=completed",
        f"transcript={question_text!r}",
        f"question_en={question_text!r}",
        f"answer_en={answer_text!r}",
        f"output_file={output_file}",
    )
    _write_last_question(question_text, answer_text)

    # Step 3: Text-to-Speech (English)
    print("Step 3: Converting answer to speech (English)...", flush=True)
    response_file, tts_time = text_to_speech(answer_text, api_key, str(output_file), lang="en")
    
    if not response_file:
        print("ERROR: Could not generate speech", flush=True)
        _write_last_question(question_text, f"{answer_text} [TTS_FAILED]")
        if FALLBACK_WAV.exists():
            shutil.copy2(FALLBACK_WAV, output_file)
            response_file = str(output_file)
            print("  ✓ Used fallback WAV (TTS failed)", flush=True)
        return str(response_file) if response_file else None
    
    total_time = time.time() - total_start_time
    print(f"Response audio saved to: {response_file}", flush=True)
    print(f"Total processing time: {total_time:.2f}s (STT: {stt_time:.2f}s, TTS: {tts_time:.2f}s)", flush=True)
    
    return str(response_file)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="English Voice Assistant - Process voice queries and generate responses"
    )
    parser.add_argument(
        "audio_file",
        nargs="?",
        help="Path to recorded audio file (WAV). Omit if using --text."
    )
    parser.add_argument(
        "-o", "--output",
        help="Output audio file path (default: response.wav in same directory)",
        default=None
    )
    parser.add_argument(
        "--text",
        help="Test mode: English question -> Q&A lookup -> TTS(English). No audio input."
    )
    
    args = parser.parse_args()
    
    if args.text:
        # Test mode: English question -> Q&A lookup -> TTS(English)
        question = args.text.strip()
        out = args.output or str(PROJECT_ROOT / "sounds" / "custom" / "response.wav")
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        api_key = get_api_key()
        print(f"Question: {question}")
        answer = find_answer(question)
        print(f"Answer (en): {answer}")
        path, _ = text_to_speech(answer, api_key, out, lang="en")
        if path:
            print(f"\n✓ Response saved: {path}")
            sys.exit(0)
        else:
            print("\n✗ TTS failed")
            sys.exit(1)
    
    if not args.audio_file:
        parser.error("Either provide audio_file or use --text")
    if not Path(args.audio_file).exists():
        print(f"ERROR: Audio file not found: {args.audio_file}")
        sys.exit(1)
    
    result = process_voice_query(
        args.audio_file,
        args.output
    )
    
    if result:
        print(f"\n✓ Success! Response audio: {result}")
        sys.exit(0)
    else:
        print("\n✗ Failed to process voice query")
        sys.exit(1)
