#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Twi greeting audio file for FreeSWITCH using Ghana NLP
This script uses the Ghana NLP API to convert Twi text to speech
"""

import os
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If dotenv not available, try to manually parse .env file
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


def generate_twi_greeting(api_key=None, output_dir="sounds/custom"):
    """
    Generate a Twi greeting audio file using Ghana NLP TTS
    
    Args:
        api_key: Ghana NLP API key (if None, will try to get from environment)
        output_dir: Directory to save the audio file
    """
    # Get API key from parameter, environment variable, or .env file
    if not api_key:
        # Try GHANANLP_API_KEY first (as specified by user), then GHANA_NLP_API_KEY
        api_key = os.getenv("GHANANLP_API_KEY") or os.getenv("GHANA_NLP_API_KEY")
    
    if not api_key:
        print("ERROR: Ghana NLP API key required!")
        print("Set it in .env file: GHANANLP_API_KEY=your_key")
        print("Or as environment variable: export GHANA_NLP_API_KEY='your_key'")
        print("Or get one from: https://translation.ghananlp.org/")
        sys.exit(1)
    
    # Initialize Ghana NLP
    try:
        nlp = GhanaNLP(api_key=api_key)
    except Exception as e:
        print(f"ERROR: Failed to initialize Ghana NLP: {e}")
        sys.exit(1)
    
    # Twi greeting text
    # "Akwaaba. Yɛma wo akwaaba wɔ FreeSWITCH." = "Welcome. We welcome you to FreeSWITCH."
    # Allow custom text via command line argument
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--text" and len(sys.argv) > 2:
        twi_text = sys.argv[2]
    else:
        twi_text = "Akwaaba. Yɛma wo akwaaba wɔ FreeSWITCH."
    
    print(f"Generating Twi TTS for: {twi_text}")
    print("Language: Twi (tw)")
    
    try:
        # Generate TTS in Twi (lang="tw")
        # The ghana-nlp library uses .tts() method
        audio_binary = nlp.tts(twi_text, lang="tw")
        
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save audio file temporarily
        temp_file = output_path / "twi_greeting_temp.wav"
        with open(temp_file, "wb") as f:
            f.write(audio_binary)
        
        # Convert to FreeSWITCH-compatible format (PCM 16-bit, 16kHz mono)
        # FreeSWITCH prefers PCM WAV format, not IEEE Float
        try:
            import subprocess
            output_file = output_path / "twi_greeting.wav"
            
            # Try using ffmpeg to convert (if available)
            try:
                subprocess.run([
                    "ffmpeg", "-i", str(temp_file),
                    "-acodec", "pcm_s16le",  # PCM 16-bit little-endian
                    "-ar", "16000",  # 16kHz sample rate
                    "-ac", "1",  # Mono
                    "-y",  # Overwrite output
                    str(output_file)
                ], check=True, capture_output=True)
                temp_file.unlink()  # Delete temp file
                print(f"  ✓ Converted audio to FreeSWITCH-compatible format")
            except (subprocess.CalledProcessError, FileNotFoundError):
                # If ffmpeg not available, try using pydub
                try:
                    from pydub import AudioSegment
                    # pydub can read various formats
                    audio = AudioSegment.from_file(str(temp_file), format="wav")
                    # Convert to PCM 16-bit, 16kHz mono
                    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
                    # Export as raw PCM WAV
                    audio.export(str(output_file), format="wav", parameters=["-acodec", "pcm_s16le"])
                    temp_file.unlink()
                    print(f"  ✓ Converted audio using pydub")
                except Exception as e1:
                    # Try soundfile + numpy resample
                    try:
                        import soundfile as sf
                        import numpy as np
                        data, sr = sf.read(str(temp_file), dtype="float64", always_2d=False)
                        if data.ndim > 1:
                            data = data.mean(axis=1)
                        target_sr = 16000
                        n = int(len(data) * target_sr / sr)
                        x_old = np.arange(len(data))
                        x_new = np.linspace(0, len(data) - 1, n)
                        data = np.interp(x_new, x_old, data).astype(np.float32)
                        sf.write(str(output_file), data, target_sr, subtype="PCM_16")
                        temp_file.unlink()
                        print(f"  ✓ Converted audio using soundfile + numpy")
                    except Exception as e2:
                        try:
                            temp_file.rename(output_file)
                            print(f"  ⚠ Warning: Audio conversion failed ({e2}). Using original format.")
                            print(f"  FreeSWITCH may not play this format. Install ffmpeg for conversion.")
                        except Exception:
                            import shutil
                            shutil.copy2(temp_file, output_file)
                            temp_file.unlink()
                            print(f"  ⚠ Warning: Using original audio format - may need manual conversion")
        except Exception as e:
            # Fallback: use file as-is
            temp_file.rename(output_file)
            print(f"  ⚠ Could not convert audio: {e}")
            print(f"  Using original format - may need manual conversion")
        
        print(f"\n✓ Success! Twi greeting saved to: {output_file}")
        print(f"\nNext steps:")
        print(f"1. Copy the file to FreeSWITCH sounds directory:")
        print(f"   Windows: Copy-Item '{output_file}' 'C:\\Program Files\\FreeSWITCH\\sounds\\custom\\twi_greeting.wav'")
        print(f"   Linux:   cp '{output_file}' /usr/share/freeswitch/sounds/en/us/callie/custom/twi_greeting.wav")
        print(f"2. Reload FreeSWITCH dialplan: fs_cli -x 'reloadxml'")
        
        return str(output_file)
        
    except Exception as e:
        print(f"ERROR: Failed to generate TTS: {e}")
        print("\nTroubleshooting:")
        print("- Verify your API key is correct")
        print("- Check your internet connection")
        print("- Ensure the Ghana NLP service is available")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate Twi greeting audio for FreeSWITCH using Ghana NLP"
    )
    parser.add_argument(
        "--api-key",
        help="Ghana NLP API key (or set GHANA_NLP_API_KEY env var)",
        default=None
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for audio file (default: sounds/custom)",
        default="sounds/custom"
    )
    parser.add_argument(
        "--text",
        help="Custom Twi text to convert (default: standard greeting)",
        default=None
    )
    
    args = parser.parse_args()
    
    # If custom text provided, modify the function call
    if args.text:
        print("Note: Custom text feature not yet implemented in this version")
        print("Using default greeting text")
    
    generate_twi_greeting(api_key=args.api_key, output_dir=args.output_dir)
