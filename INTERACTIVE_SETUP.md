# Interactive Voice Assistant Setup

## Overview

Extension **1002** is now configured as an interactive voice assistant that can:
1. Play a Twi greeting
2. Record your question
3. Process it using Ghana NLP (Speech-to-Text)
4. Generate an answer
5. Speak the answer back in Twi

## How It Works

### Call Flow:
1. **Dial 1002** from your SIP client
2. **Hear greeting**: "Akwaaba. Yɛma wo akwaaba wɔ FreeSWITCH."
3. **Ask your question** in Twi (you have up to 20 seconds)
4. **Wait for processing** (a few seconds)
5. **Hear the answer** in Twi

### Technical Flow:
1. FreeSWITCH records your voice to `/tmp/user_question.wav`
2. Python script (`voice_assistant.py`) processes it:
   - Converts speech to text using Ghana NLP STT
   - Processes the question (keyword matching for now)
   - Generates answer in Twi
   - Converts answer to speech using Ghana NLP TTS
3. FreeSWITCH plays the response audio

## Current Q&A Capabilities

The system currently uses simple keyword matching. It understands:

- **"wo ho te sɛn"** / **"wo ho te sen"** (How are you?)
  - Response: "Me ho ye. Meda wo ase sɛ wobu me. Wo ho te sɛn?"

- **"ɛte sɛn"** (How is it?)
  - Response: "Ɛyɛ. Me ho ye. Ɛte sɛn wo nso?"

- **"akwaaba"** (Welcome)
  - Response: "Meda wo ase. Yɛma wo akwaaba!"

- **"meda wo ase"** (Thank you)
  - Response: "Mepa wo kyɛw. Ɛyɛ me anigyeɛ sɛ meka wo ho."

- **"me din"** / **"wo din"** (What is your name?)
  - Response: "Me din ne Cultiflow Voice Assistant. Me bɛboa wo sɛn?"

- **"help"** / **"boa me"** (Help me)
  - Response: "Mepɛ sɛ meboa wo. Ka me sɛn na ɛsɛ sɛ meyɛ ma wo."

- **Default**: If question doesn't match, responds with:
  - "Meda wo ase sɛ wobu me. Mepɛ sɛ meboa wo, nanso me nte asɛm no yi yiye. San ka bio, anaa ka me sɛn na ɛsɛ sɛ meyɛ ma wo."

## Testing

1. **Register** your SIP client (MicroSIP) with extension 1000
2. **Dial 1002**
3. **Wait** for the greeting
4. **Ask a question** in Twi (try: "wo ho te sɛn?")
5. **Wait** for the response

## Troubleshooting

### No Response After Asking Question:
- Check FreeSWITCH console logs for errors
- Verify Python script path is correct in dialplan
- Check if `/tmp/user_question.wav` was created
- Verify Ghana NLP API key is set

### Can't Hear Recording Prompt:
- The system records immediately after the greeting
- Speak your question right after hearing the greeting
- You have up to 20 seconds, or it stops after 3 seconds of silence

### Response Takes Too Long:
- Speech-to-text processing takes a few seconds
- Text-to-speech generation takes a few seconds
- Total processing time: ~5-10 seconds

### Want to Add More Questions:
Edit `voice_assistant.py` and add to the `responses` dictionary in the `process_question()` function.

## Next Steps: Adding AI/LLM

To make the assistant smarter, you can integrate an LLM:

1. **OpenAI GPT**: Add OpenAI API key and modify `process_question()` to call GPT
2. **Ollama (Local)**: Run Ollama locally and call it from Python
3. **Other LLMs**: Integrate any LLM API

Example integration in `voice_assistant.py`:
```python
def process_question(question_text, lang="tw"):
    # Translate to English if needed
    # Call LLM API
    # Translate response back to Twi
    # Return answer
```

## Files

- **voice_assistant.py**: Main processing script (STT -> Q&A -> TTS)
- **conf/dialplan/default.xml**: FreeSWITCH dialplan with extension 1002
- **generate_twi_greeting.py**: Script to generate greeting audio

## Requirements

- Python 3.7+
- ghana-nlp package
- soundfile package (for audio conversion)
- Ghana NLP API key in `.env` file
