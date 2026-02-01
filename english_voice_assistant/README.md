# English Voice Assistant

A simplified voice assistant that handles English speech-to-text, question matching, and text-to-speech responses using hardcoded Q&A pairs.

## Features

- **English-only**: Caller speaks English, system responds in English
- **No database**: Uses hardcoded Q&A pairs defined in `voice_assistant.py`
- **Simple matching**: Exact match, partial match, and keyword matching
- **Ghana NLP integration**: Uses Ghana NLP API for STT and TTS

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API key**:
   Create a `.env` file in this directory (or use the parent directory's `.env`):
   ```
   GHANANLP_API_KEY=your_api_key_here
   ```

3. **Add Q&A pairs**:
   Edit `voice_assistant.py` and modify the `QA_PAIRS` dictionary to add your question-answer pairs.

## Usage

### Test with text input:
```bash
python voice_assistant.py --text "hello"
```

### Process audio file:
```bash
python voice_assistant.py path/to/audio.wav
```

### Specify output file:
```bash
python voice_assistant.py path/to/audio.wav -o response.wav
```

## How It Works

1. **Speech-to-Text**: Converts English audio to text using Ghana NLP STT
2. **Question Matching**: Matches the transcribed question against hardcoded Q&A pairs:
   - First tries exact match
   - Then tries partial match (question contains key phrase)
   - Finally tries keyword matching
   - Falls back to default message if no match
3. **Text-to-Speech**: Converts the answer to English speech using Ghana NLP TTS

## Adding Q&A Pairs

Edit the `QA_PAIRS` dictionary in `voice_assistant.py`:

```python
QA_PAIRS = {
    "your question": "Your answer here",
    "another question": "Another answer",
    # ... more pairs
}
```

For keyword-based matching, add entries to `QA_KEYWORDS`:

```python
QA_KEYWORDS = {
    "keyword": "Answer when keyword is found in question",
    # ... more keywords
}
```

## Logs

Logs are written to:
- `C:\Users\User\Desktop\Recordings\last_call_log.txt` - Last call details
- `C:\Users\User\Desktop\Recordings\live_log.txt` - Live call log (append mode)
- `C:\Users\User\Desktop\Recordings\last_question.txt` - Last question and answer

## Differences from Twi Version

- **No translation**: No Twi-English translation needed
- **No database**: Uses hardcoded Q&A pairs instead of SQLite/PostgreSQL
- **English only**: STT and TTS both use English (`lang="en"`)
- **Simpler flow**: Direct question matching without translation steps
