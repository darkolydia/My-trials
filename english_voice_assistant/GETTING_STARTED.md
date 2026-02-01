# Getting Started with English Voice Assistant

This guide will help you set up and start using the English Voice Assistant quickly.

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Ghana NLP API Key** - Get one at https://translation.ghananlp.org/
3. **Windows PowerShell** (for Windows users)

## Step-by-Step Setup

### Step 1: Navigate to the English Voice Assistant Folder

```powershell
cd "C:\Users\User\Desktop\FreeSWITCH-to-linphone\english_voice_assistant"
```

### Step 2: Install Dependencies

```powershell
pip install -r requirements.txt
```

This will install:
- `ghana-nlp` - For speech-to-text and text-to-speech
- `pydub` - For audio processing
- `python-dotenv` - For environment variable management

### Step 3: Set Up Your API Key

You have two options:

**Option A: Use parent directory's .env file** (if it exists)
- The script will automatically check the parent directory for `.env`
- Make sure it contains: `GHANANLP_API_KEY=your_api_key_here`

**Option B: Create a new .env file in this folder**

Create a file named `.env` in the `english_voice_assistant` folder:

```powershell
# Create .env file
echo "GHANANLP_API_KEY=your_api_key_here" > .env
```

Replace `your_api_key_here` with your actual Ghana NLP API key.

### Step 4: Test the Setup

Test with a text question (no audio needed):

```powershell
python voice_assistant.py --text "hello"
```

This will:
1. Match "hello" to a Q&A pair
2. Generate English speech audio
3. Save it to `sounds/custom/response.wav`

**Expected output:**
```
Question: hello
Answer (en): Hello! How can I help you today?
✓ TTS -> FreeSWITCH WAV
✓ Response saved: C:\Users\User\Desktop\FreeSWITCH-to-linphone\english_voice_assistant\sounds\custom\response.wav
```

### Step 5: View Available Q&A Pairs

See what questions are already configured:

```powershell
python manage_qa.py --list
```

### Step 6: Test Q&A Matching

Test how different questions are matched:

```powershell
python manage_qa.py --test "what is your name"
python manage_qa.py --test "where are you located"
python test_qa.py
```

## Adding Your Own Q&A Pairs

### Method 1: Edit voice_assistant.py

Open `voice_assistant.py` and find the `QA_PAIRS` dictionary (around line 73). Add your questions:

```python
QA_PAIRS = {
    # ... existing pairs ...
    
    # Your custom pairs
    "what are your hours": "We are open Monday to Friday, 9 AM to 5 PM.",
    "what is your phone number": "You can reach us at 555-1234.",
    "how do I contact support": "Please email us at support@example.com.",
}
```

### Method 2: Add Keyword-Based Answers

For flexible matching, add to `QA_KEYWORDS` dictionary:

```python
QA_KEYWORDS = {
    # ... existing keywords ...
    
    # Your keywords
    "hours": "We are open Monday to Friday, 9 AM to 5 PM.",
    "phone": "You can reach us at 555-1234.",
    "support": "Please email us at support@example.com.",
}
```

## Testing with Audio Files

### Option 1: Record an Audio File

Record a WAV file (16kHz, 16-bit, mono recommended) and test:

```powershell
python voice_assistant.py "path/to/your/audio.wav"
```

### Option 2: Use Test Audio

If you have a test audio file:

```powershell
python voice_assistant.py "C:\path\to\test_audio.wav" -o response.wav
```

## Integration with FreeSWITCH

To use this with FreeSWITCH:

1. **Update FreeSWITCH dialplan** to call the English voice assistant script
2. **Point to the correct path**: `C:\Users\User\Desktop\FreeSWITCH-to-linphone\english_voice_assistant\voice_assistant.py`
3. **Ensure audio format**: The script outputs 16kHz 16-bit mono WAV files compatible with FreeSWITCH

Example dialplan snippet:
```xml
<action application="python" data="C:\Users\User\Desktop\FreeSWITCH-to-linphone\english_voice_assistant\voice_assistant.py ${record_file}"/>
<action application="playback" data="C:\Users\User\Desktop\FreeSWITCH-to-linphone\english_voice_assistant\sounds\custom\response.wav"/>
```

## Troubleshooting

### Error: "ghana-nlp package not installed"
```powershell
pip install ghana-nlp
```

### Error: "Ghana NLP API key required!"
- Check that your `.env` file exists and contains `GHANANLP_API_KEY=your_key`
- Or set it as an environment variable:
  ```powershell
  $env:GHANANLP_API_KEY = "your_api_key_here"
  ```

### Error: "TTS conversion failed"
Install audio conversion tools:
```powershell
# Option 1: Install ffmpeg
# Download from https://ffmpeg.org/download.html

# Option 2: Install pydub (already in requirements.txt)
pip install pydub
```

### Audio file not found
- Make sure the audio file path is correct
- Use absolute paths if relative paths don't work
- Check file permissions

## Next Steps

1. **Customize Q&A pairs** - Add your own questions and answers
2. **Test thoroughly** - Try various questions to ensure matching works
3. **Integrate with FreeSWITCH** - Connect it to your phone system
4. **Monitor logs** - Check `C:\Users\User\Desktop\Recordings\` for call logs

## Quick Reference

| Command | Description |
|---------|-------------|
| `python voice_assistant.py --text "question"` | Test with text (no audio) |
| `python voice_assistant.py audio.wav` | Process audio file |
| `python manage_qa.py --list` | List all Q&A pairs |
| `python manage_qa.py --test "question"` | Test question matching |
| `python test_qa.py` | Run all test questions |

## Need Help?

- Check the main `README.md` in this folder
- Review the `voice_assistant.py` code comments
- Check logs in `C:\Users\User\Desktop\Recordings\`
