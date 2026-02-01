#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voice Assistant - Interactive Q&A System
Handles: Speech-to-Text -> Question Processing -> Text-to-Speech

Flow: User speaks -> STT(Twi) -> translate tw-en -> lookup English Q&A (SQLite) -> en-tw -> TTS(Twi).
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path
from datetime import datetime

# Project root = directory containing this script (used for DB and .env when run by FreeSWITCH)
PROJECT_ROOT = Path(__file__).resolve().parent
# When TTS fails, copy this to response.wav so we don't replay the previous answer
FALLBACK_WAV = PROJECT_ROOT / "sounds" / "custom" / "twi_please_wait.wav"
# Fixed recordings dir for logs (always write here so you can open files after each call)
RECORDINGS_DIR = Path(r"C:\Users\User\Desktop\Recordings")

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load .env from project root (so it works when FreeSWITCH runs script from a different CWD)
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

# Import database module
try:
    from database import VoiceAssistantDB, get_db
    DB_AVAILABLE = True
except ImportError:
    print("WARNING: database module not available. Database logging disabled.")
    DB_AVAILABLE = False


def get_api_key():
    """Get Ghana NLP API key from environment"""
    api_key = os.getenv("GHANANLP_API_KEY") or os.getenv("GHANA_NLP_API_KEY")
    if not api_key:
        print("ERROR: Ghana NLP API key required!")
        print("Set it in .env file: GHANANLP_API_KEY=your_key")
        sys.exit(1)
    return api_key


# User speaks English; we lookup English Q&A and speak the answer in Twi.


def translate_text(text, language_pair, api_key):
    """
    Translate text using Ghana NLP (e.g. tw-en or en-tw).
    Returns (translated string or None, processing time in seconds).
    """
    if not (text or "").strip():
        return None, 0.0
    start = time.time()
    try:
        nlp = GhanaNLP(api_key=api_key)
        if not hasattr(nlp, "translate"):
            return None, time.time() - start
        result = nlp.translate((text or "").strip(), language_pair=language_pair)
        elapsed = time.time() - start
        if isinstance(result, str) and result.strip():
            return result.strip(), elapsed
        if isinstance(result, dict):
            out = result.get("translation", result.get("text", ""))
            if out and str(out).strip():
                return str(out).strip(), elapsed
        return None, elapsed
    except Exception as e:
        print(f"WARNING: Translation ({language_pair}) failed: {e}", flush=True)
        return None, time.time() - start


def speech_to_text(audio_file, api_key, lang="tw"):
    """
    Convert speech audio to text using Ghana NLP ASR
    
    Args:
        audio_file: Path to audio file (WAV format)
        api_key: Ghana NLP API key
        lang: Language code (tw for Twi)
    
    Returns:
        Tuple of (transcribed text string, processing time in seconds)
    """
    start_time = time.time()
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


def process_question(question_text, lang="en", db=None):
    """
    Look up the question in the database only. No priority logic, no keywords.
    Returns DB answer or default if no match.
    """
    q = (question_text or "").strip().lower()
    print(f"[Q&A] question: {q!r}", flush=True)
    default = "Thank you for calling. I did not understand that clearly. Please say again, or tell me what you need."

    if not db or not DB_AVAILABLE:
        print("[Q&A] no database, using default", flush=True)
        return default

    try:
        for try_lang in ("en", "tw"):
            qa = db.find_qa_pair(question_text, language=try_lang)
            if qa:
                print(f"[Q&A] DB match qa_id={qa['qa_id']} lang={try_lang}", flush=True)
                return qa["answer_text"]
    except Exception as e:
        print(f"WARNING: Database lookup failed: {e}", flush=True)

    print("[Q&A] no match, using default", flush=True)
    return default


def _convert_to_wav(temp_path: Path, out_path: Path) -> bool:
    """Convert temp audio (WAV from Ghana TTS) to 16kHz 16-bit mono. Overwrites out_path."""
    out_path = Path(out_path)
    if out_path.exists():
        try:
            out_path.unlink()
        except Exception:
            pass
    # 1. soundfile (Ghana TTS returns WAV) – same as generate_twi_greeting
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
    except Exception:
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
    # 3. pydub
    for fmt in ("wav", "mp3"):
        try:
            from pydub import AudioSegment
            seg = AudioSegment.from_file(str(temp_path), format=fmt)
            seg = seg.set_frame_rate(16000).set_channels(1).set_sample_width(2)
            seg.export(str(out_path), format="wav")
            return True
        except Exception:
            pass
    return False


def text_to_speech(text, api_key, output_file, lang="tw"):
    """Ghana NLP TTS -> WAV. Converts to 16kHz 16-bit mono for FreeSWITCH."""
    start_time = time.time()
    try:
        nlp = GhanaNLP(api_key=api_key)
        raw = nlp.tts(text, lang=lang)
        if isinstance(raw, dict):
            print(f"ERROR: TTS API error: {raw.get('message', raw)}", flush=True)
            return None, time.time() - start_time
        out = Path(output_file)
        out.parent.mkdir(parents=True, exist_ok=True)
        temp = out.parent / f"temp_tts_{out.stem}.wav"
        with open(temp, "wb") as f:
            f.write(raw)
        if _convert_to_wav(temp, out):
            try:
                temp.unlink()
            except Exception:
                pass
            print(f"  ✓ TTS -> FreeSWITCH WAV", flush=True)
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


def process_voice_query(audio_file, output_file=None, call_id=None, caller_id=None, extension="1002"):
    """
    Main function: Process a voice query and generate response audio
    
    Flow:
    1. Speech-to-Text: Convert audio to text
    2. Process Question: Generate answer
    3. Text-to-Speech: Convert answer to audio
    4. Database Logging: Store call and conversation data
    
    Args:
        audio_file: Path to recorded audio file
        output_file: Path to save response audio (optional)
        call_id: Existing call ID (if None, creates new call record)
        caller_id: SIP caller ID (optional)
        extension: Extension number called (default: 1002)
    
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
    
    # Logs: always use fixed RECORDINGS_DIR so you can open them after each call
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

    def _write_last_question(twi: str, en: str, ans: str) -> None:
        """Overwrite last_question.txt so you can open it in Notepad after each call."""
        try:
            rec.mkdir(parents=True, exist_ok=True)
            with open(last_q_path, "w", encoding="utf-8") as f:
                f.write(f"transcript_twi: {twi}\n")
                f.write(f"question_en: {en}\n")
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
    _write_last_question("(starting...)", "(starting...)", "")
    
    # Overwrite response.wav immediately so we never play stale audio (e.g. old who-owns)
    if FALLBACK_WAV.exists():
        try:
            shutil.copy2(FALLBACK_WAV, output_file)
            print("Cleared response.wav with fallback (will overwrite with real TTS)", flush=True)
        except Exception as e:
            print(f"WARNING: Could not clear response.wav: {e}", flush=True)
    
    api_key = get_api_key()
    
    # Use DB in project root so FreeSWITCH (different CWD) uses same DB as manage_qa
    db_path = str(PROJECT_ROOT / "voice_assistant.db")
    db = None
    if DB_AVAILABLE:
        try:
            db = get_db(db_path)
            # Create call record if call_id not provided
            if call_id is None:
                call_id = db.create_call(
                    caller_id=caller_id,
                    extension=extension,
                    audio_file_path=str(audio_file)
                )
                print(f"Created call record: call_id={call_id}", flush=True)
        except Exception as e:
            print(f"WARNING: Database error: {e}", flush=True)
            db = None
    
    print(f"Processing voice query from: {audio_file}", flush=True)
    
    # Step 1: Speech-to-Text (Twi only). You speak Twi → we translate to English for DB lookup.
    print("Step 1: Converting speech to text (Twi)...", flush=True)
    transcript_twi, stt_time = speech_to_text(audio_file, api_key, lang="tw")
    
    if not transcript_twi:
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
        _write_last_question("(STT failed)", "[STT_FAILED]", "[STT_FAILED]")
        print("ERROR: Could not transcribe speech", flush=True)
        _write_log(
            f"timestamp={datetime.now().isoformat()}",
            "status=stt_failed",
            "transcript_twi=None",
            "question_en=[STT_FAILED]",
            "answer_en=[STT_FAILED]",
            f"output_file={output_file}",
        )
        error_text = "Mepa wo kyɛw, me nte asɛm no yi yiye. San ka bio."
        response_file, tts_time = text_to_speech(error_text, api_key, str(output_file), lang="tw")
        if not response_file and FALLBACK_WAV.exists():
            shutil.copy2(FALLBACK_WAV, output_file)
            response_file = str(output_file)
            print("  ✓ Used fallback WAV (TTS failed)", flush=True)
        if db and call_id:
            try:
                db.add_conversation(
                    call_id=call_id,
                    question_text="[STT_FAILED]",
                    answer_text=error_text,
                    question_audio_path=str(audio_file),
                    answer_audio_path=str(response_file) if response_file else None,
                    stt_processing_time=stt_time,
                    tts_processing_time=tts_time,
                    total_processing_time=time.time() - total_start_time,
                    language="tw"
                )
                db.update_call(call_id, status="failed", response_file_path=str(response_file) if response_file else None)
            except Exception as e:
                print(f"WARNING: Failed to log conversation: {e}", flush=True)
        return str(response_file) if response_file else None
    
    # Step 2: Translate Twi -> English, then DB lookup
    question_text = str(transcript_twi or "").strip()
    transcript_raw = transcript_twi
    q_en, _ = translate_text(transcript_twi, "tw-en", api_key)
    if q_en and str(q_en).strip():
        question_text = str(q_en).strip()

    # Log your question (terminal when run manually; tail live_log.txt when FreeSWITCH runs it)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    block = [
        "",
        f">>> {ts}",
        "=" * 60,
        "  YOUR QUESTION (transcribed)",
        "=" * 60,
        f"  Twi:     {transcript_raw}",
        f"  English: {question_text}",
        "=" * 60,
        "",
    ]
    for line in block:
        print(line, flush=True)
    _append_live(*block)

    print("Step 2: Processing question (English lookup)...", flush=True)
    answer_text = process_question(question_text, lang="en", db=db)
    print(f"Generated answer (en): {answer_text}", flush=True)

    _write_log(
        f"timestamp={datetime.now().isoformat()}",
        "status=completed",
        f"transcript={transcript_raw!r}",
        f"question_en={question_text!r}",
        f"answer_en={answer_text!r}",
        f"output_file={output_file}",
    )
    _write_last_question(str(transcript_raw or ""), question_text, answer_text)

    # Step 3: Translate answer to Twi, then TTS (Twi)
    speak_text = answer_text
    answer_twi, _ = translate_text(answer_text, "en-tw", api_key)
    if answer_twi:
        speak_text = answer_twi
        print(f"Translated (Twi): {speak_text}", flush=True)
    else:
        print("WARNING: en-tw translation failed, speaking English", flush=True)
    print("Step 3: Converting answer to speech (Twi)...", flush=True)
    response_file, tts_time = text_to_speech(speak_text, api_key, str(output_file), lang="tw")
    
    if not response_file:
        print("ERROR: Could not generate speech", flush=True)
        _write_last_question(str(transcript_raw or ""), question_text, f"{answer_text} [TTS_FAILED]")
        if FALLBACK_WAV.exists():
            shutil.copy2(FALLBACK_WAV, output_file)
            response_file = str(output_file)
            print("  ✓ Used fallback WAV (TTS failed)", flush=True)
        if db and call_id:
            try:
                db.add_conversation(
                    call_id=call_id,
                    question_text=question_text,
                    answer_text="[TTS_FAILED]",
                    question_audio_path=str(audio_file),
                    stt_processing_time=stt_time,
                    tts_processing_time=tts_time,
                    total_processing_time=time.time() - total_start_time,
                    language="tw"
                )
                db.update_call(call_id, status="failed")
            except Exception as e:
                print(f"WARNING: Failed to log conversation: {e}", flush=True)
        return str(response_file) if response_file else None
    
    total_time = time.time() - total_start_time
    print(f"Response audio saved to: {response_file}", flush=True)
    print(f"Total processing time: {total_time:.2f}s (STT: {stt_time:.2f}s, TTS: {tts_time:.2f}s)", flush=True)
    
    if db and call_id:
        try:
            db.add_conversation(
                call_id=call_id,
                question_text=question_text,
                answer_text=answer_text,
                question_audio_path=str(audio_file),
                answer_audio_path=str(response_file),
                stt_processing_time=stt_time,
                tts_processing_time=tts_time,
                total_processing_time=total_time,
                language="tw"
            )
            db.update_call(
                call_id=call_id,
                status="completed",
                response_file_path=str(response_file),
                duration_seconds=int(total_time)
            )
            print(f"Logged conversation to database (call_id={call_id})", flush=True)
        except Exception as e:
            print(f"WARNING: Failed to log conversation: {e}", flush=True)
    
    return str(response_file)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Voice Assistant - Process voice queries and generate responses"
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
        help="Test mode: English question -> SQLite lookup -> translate to Twi -> TTS(Twi). No audio input."
    )
    parser.add_argument(
        "--call-id",
        type=int,
        help="Existing call ID for database tracking (optional)",
        default=None
    )
    parser.add_argument(
        "--caller-id",
        help="SIP caller ID for database tracking (optional)",
        default=None
    )
    parser.add_argument(
        "--extension",
        help="Extension number called (default: 1002)",
        default="1002"
    )
    
    args = parser.parse_args()
    
    if args.text:
        # Test mode: English question -> SQLite lookup -> translate to Twi -> TTS(Twi)
        question = args.text.strip()
        out = args.output or str(PROJECT_ROOT / "sounds" / "custom" / "response.wav")
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        api_key = get_api_key()
        db = get_db(str(PROJECT_ROOT / "voice_assistant.db")) if DB_AVAILABLE else None
        print(f"Question: {question}")
        answer = process_question(question, lang="en", db=db)
        print(f"Answer (en): {answer}")
        speak = answer
        twi, _ = translate_text(answer, "en-tw", api_key)
        if twi:
            speak = twi
            print(f"Translated (Twi): {speak}")
        path, _ = text_to_speech(speak, api_key, out, lang="tw")
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
        args.output,
        call_id=args.call_id,
        caller_id=args.caller_id,
        extension=args.extension
    )
    
    if result:
        print(f"\n✓ Success! Response audio: {result}")
        sys.exit(0)
    else:
        print("\n✗ Failed to process voice query")
        sys.exit(1)
