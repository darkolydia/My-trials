# End-to-End Data Flow
## Voice Assistant System - Simple Overview

---

## Complete Flow (Extension 1002)

1. **User dials 1002** from SIP client (Linphone/MicroSIP)
   - SIP INVITE sent to FreeSWITCH server

2. **FreeSWITCH receives call**
   - Matches dialplan for extension 1002
   - Routes to extension_1002 handler

3. **Call answered**
   - FreeSWITCH sends SIP 200 OK
   - RTP audio channels established

4. **Greeting played**
   - FreeSWITCH plays: `twi_greeting.wav`
   - User hears: "Akwaaba. Yɛma wo akwaaba wɔ FreeSWITCH."

5. **User question recorded**
   - FreeSWITCH plays beep and records user's voice
   - Audio saved to: `C:/freeswitch_recordings/user_question.wav`
   - Recording stops after 3 seconds silence or 20 seconds max

6. **"Please wait" message played**
   - FreeSWITCH plays: `twi_please_wait.wav`
   - User hears: "Mepa wo kyɛw, sua. Mɛyɛ adwuma no."

7. **Python script invoked**
   - FreeSWITCH calls: `python voice_assistant.py user_question.wav -o response.wav`
   - Script processes audio asynchronously

8. **Speech-to-Text (STT)**
   - Python reads: `user_question.wav`
   - Sends audio to Ghana NLP STT API
   - Receives transcribed text (e.g., "wo ho te sen")

9. **Question processing**
   - Python matches keywords against response dictionary
   - Generates answer text in Twi
   - Example: "Me ho ye. Meda wo ase sɛ wobu me. Wo ho te sɛn?"

10. **Text-to-Speech (TTS)**
    - Python sends answer text to Ghana NLP TTS API
    - Receives synthesized speech audio
    - Converts to FreeSWITCH format (16kHz, 16-bit PCM, mono)
    - Saves to: `C:/Program Files/FreeSWITCH/sounds/custom/response.wav`

11. **Response played**
    - FreeSWITCH plays: `response.wav`
    - User hears the answer in Twi

12. **Call ends**
    - FreeSWITCH sends SIP BYE
    - Call terminated, resources released

---

## Components

- **SIP Client**: User's phone app (Linphone/MicroSIP)
- **FreeSWITCH**: Telephony server handling calls, recording, playback
- **Python Script**: Processes audio (STT → Q&A → TTS)
- **Ghana NLP API**: Provides Twi speech-to-text and text-to-speech services

---

## Data Formats

- **Input Recording**: WAV (16-bit, 16kHz, mono)
- **Output Response**: WAV (16-bit, 16kHz, mono)
- **Network**: SIP (signaling), RTP (audio stream)
- **API**: HTTP/HTTPS (Ghana NLP services)

---

## Timing

- **Total Call Duration**: ~15-21 seconds
  - Recording: ~3-5 seconds
  - STT Processing: ~3-5 seconds
  - TTS Processing: ~3-5 seconds
  - Playback: ~2-4 seconds
