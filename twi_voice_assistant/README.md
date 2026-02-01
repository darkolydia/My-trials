# Twi Voice Assistant (Original Version)

This folder contains the **original Twi voice assistant** with database integration.

## Features

- **Twi Language Support**: Caller speaks Twi, system responds in Twi
- **Database Integration**: Uses SQLite/PostgreSQL database for Q&A pairs
- **Translation**: Automatic Twi ↔ English translation using Ghana NLP
- **Full Logging**: Database logging of all calls and conversations

## Flow

1. User speaks Twi → STT(Twi)
2. Translate Twi → English
3. Lookup Q&A in database (English)
4. Translate answer English → Twi
5. TTS(Twi) → Response audio

## Key Files

- `voice_assistant.py` - Main voice assistant script
- `database.py` - Database module for Q&A storage
- `manage_qa.py` - Script to manage Q&A pairs in database
- `qa_store.py` - Q&A store interface
- `view_database.py` - View database contents
- `reset_qa.py` - Reset Q&A database
- `generate_twi_greeting.py` - Generate Twi greeting audio
- `play_twi_phrase.py` - Test Twi TTS

## Documentation

- `DATABASE_INTEGRATION.md` - Database integration guide
- `QA_DATABASE_FEATURE.md` - Q&A database feature documentation
- `END_TO_END_DATA_FLOW.md` - End-to-end data flow documentation

## Differences from English Version

| Feature | Twi Version | English Version |
|---------|-------------|-----------------|
| Language | Twi (with translation) | English only |
| Q&A Storage | Database (SQLite/PostgreSQL) | Hardcoded dictionary |
| Translation | Yes (Twi ↔ English) | No |
| Database Logging | Yes | No |
| Complexity | Higher | Lower |

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up database (see `DATABASE_INTEGRATION.md`)

3. Configure `.env` file with `GHANANLP_API_KEY`

4. Add Q&A pairs using `manage_qa.py`

## Usage

See the main project README.md in the parent directory for general setup instructions.
