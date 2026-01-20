# Voice Assistant System Architecture

## Overview

This is a call-based voice AI assistant that allows users to interact with an intelligent system through phone calls. The system understands Twi (a Ghanaian language) and responds in Twi.

## System Components

### 1. FreeSWITCH (SIP Server/PBX)
- **Role**: Handles call routing, audio recording, and playback
- **Location**: `C:\Program Files\FreeSWITCH\`
- **Key Functions**:
  - Receives SIP calls from clients (MicroSIP, Linphone)
  - Routes calls based on dialplan
  - Records user's voice
  - Plays audio responses
  - Manages call state

### 2. SIP Client (MicroSIP/Linphone)
- **Role**: User's phone application
- **Function**: Makes calls to FreeSWITCH extensions

### 3. Python Voice Assistant (`voice_assistant.py`)
- **Role**: Processes voice queries and generates responses
- **Location**: `C:\Users\User\Desktop\FreeSWITCH-to-linphone\voice_assistant.py`
- **Key Functions**:
  - Speech-to-Text (STT) using Ghana NLP
  - Question processing and answer generation
  - Text-to-Speech (TTS) using Ghana NLP
  - Audio format conversion

### 4. Ghana NLP API
- **Role**: Provides Twi language processing
- **Services Used**:
  - **STT (Speech-to-Text)**: Converts Twi speech to text
  - **TTS (Text-to-Speech)**: Converts Twi text to speech
- **API Key**: Stored in `.env` file

## Complete Call Flow

### When User Dials 1002:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER DIALS 1002                                          │
│    (From MicroSIP/Linphone)                                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. FREESWITCH RECEIVES CALL                                 │
│    - Checks dialplan for extension 1002                     │
│    - Matches extension_1002                                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. CALL ANSWERED                                            │
│    - FreeSWITCH answers the call                           │
│    - Waits 1 second for call to stabilize                  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. PLAY GREETING                                            │
│    - Plays: "Akwaaba. Yɛma wo akwaaba wɔ FreeSWITCH."      │
│    - File: C:/Program Files/FreeSWITCH/sounds/custom/      │
│            twi_greeting.wav                                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. RECORD USER'S QUESTION                                   │
│    - Plays BEEP (recording starts)                         │
│    - Records up to 20 seconds                              │
│    - Stops after 3 seconds of silence                      │
│    - Saves to: C:/freeswitch_recordings/user_question.wav │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. PLAY "PLEASE WAIT" MESSAGE                              │
│    - Plays: "Mepa wo kyɛw, sua. Mɛyɛ adwuma no."          │
│    - File: C:/Program Files/FreeSWITCH/sounds/custom/      │
│            twi_please_wait.wav                             │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. PROCESS VOICE QUERY                                      │
│    FreeSWITCH calls Python script:                          │
│    python voice_assistant.py [audio_file] -o [output]      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. SPEECH-TO-TEXT (STT)                                     │
│    - voice_assistant.py reads audio file                    │
│    - Calls Ghana NLP STT API                                │
│    - Converts Twi speech → Twi text                        │
│    - Example: "wo ho te sen?" → "wo ho te sen"            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 9. QUESTION PROCESSING                                      │
│    - Analyzes transcribed text                              │
│    - Matches keywords (e.g., "wo ho te sen")               │
│    - Generates appropriate response in Twi                  │
│    - Example response: "Me ho ye. Meda wo ase..."          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 10. TEXT-TO-SPEECH (TTS)                                    │
│     - Calls Ghana NLP TTS API                               │
│     - Converts Twi text → Twi speech                        │
│     - Saves as: response.wav                               │
│     - Converts to PCM 16-bit, 16kHz mono format            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 11. PLAY RESPONSE                                           │
│     - FreeSWITCH plays response.wav                         │
│     - User hears answer in Twi                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 12. CALL ENDS                                               │
│     - FreeSWITCH hangs up                                   │
│     - Call completed                                        │
└─────────────────────────────────────────────────────────────┘
```

## File Locations

### Configuration Files
- **Dialplan**: `C:\Program Files\FreeSWITCH\conf\dialplan\default.xml`
- **Directory**: `C:\Program Files\FreeSWITCH\conf\directory\default.xml`
- **Python Script**: `C:\Users\User\Desktop\FreeSWITCH-to-linphone\voice_assistant.py`

### Audio Files
- **Greeting**: `C:\Program Files\FreeSWITCH\sounds\custom\twi_greeting.wav`
- **Please Wait**: `C:\Program Files\FreeSWITCH\sounds\custom\twi_please_wait.wav`
- **Response**: `C:\Program Files\FreeSWITCH\sounds\custom\response.wav` (generated)

### Recordings
- **User Questions**: `C:\freeswitch_recordings\user_question.wav`

## Extensions

### Extension 1000
- Simple greeting in English
- Uses FreeSWITCH built-in TTS (Flite)

### Extension 1001
- Twi greeting
- Plays pre-generated Twi audio file

### Extension 1002 (Interactive Voice Assistant)
- Full Q&A system
- Records user question
- Processes and responds in Twi

## Supported Questions (Current)

The system uses keyword matching. It understands:

| Twi Question | English | Response |
|--------------|---------|----------|
| "wo ho te sɛn" | "How are you?" | "Me ho ye. Meda wo ase..." |
| "akwaaba" | "Welcome" | "Meda wo ase. Yɛma wo akwaaba!" |
| "me din" / "wo din" | "What is your name?" | "Me din ne Cultiflow Voice Assistant..." |
| "help" / "boa me" | "Help me" | "Mepɛ sɛ meboa wo..." |
| (default) | Any other question | "Meda wo ase sɛ wobu me. Mepɛ sɛ meboa wo..." |

## Processing Time

- **Recording**: ~3-5 seconds (user speaks)
- **STT Processing**: ~3-5 seconds (Ghana NLP API)
- **Question Processing**: <1 second (local)
- **TTS Processing**: ~3-5 seconds (Ghana NLP API)
- **Audio Conversion**: ~1 second
- **Total**: ~7-11 seconds

## Technology Stack

1. **FreeSWITCH**: Open-source telephony platform
2. **SIP (Session Initiation Protocol)**: For call signaling
3. **RTP (Real-time Transport Protocol)**: For audio transmission
4. **Python 3**: Processing script language
5. **Ghana NLP API**: Twi language processing
6. **soundfile**: Audio format conversion

## Future Enhancements

1. **LLM Integration**: Replace keyword matching with AI (OpenAI, Ollama)
2. **Multi-turn Conversation**: Keep call open for multiple questions
3. **Better STT Accuracy**: Fine-tune or use better models
4. **Response Caching**: Cache common responses for faster replies
5. **Database Integration**: Store conversation history
6. **More Languages**: Support other Ghanaian languages (Ga, Ewe)

## Troubleshooting

### If recording doesn't work:
- Check file path (no spaces)
- Verify directory permissions
- Check FreeSWITCH logs

### If processing fails:
- Verify Ghana NLP API key in `.env`
- Check Python script path in dialplan
- Review FreeSWITCH console logs

### If no response:
- Check if `response.wav` was created
- Verify audio file format (PCM 16-bit, 16kHz)
- Check FreeSWITCH playback logs
