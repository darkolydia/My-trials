# Ghana NLP Integration for Twi Greetings

This guide explains how to integrate Ghana NLP to generate Twi (Akan) greetings for FreeSWITCH instead of English TTS.

## Overview

FreeSWITCH's built-in TTS engine (`mod_flite`) does not support Ghanaian languages like Twi. To provide greetings in Twi, we use the **Ghana NLP API** to generate audio files that FreeSWITCH can play.

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Ghana NLP API Key** - Get one from: https://translation.ghananlp.org/
3. **FreeSWITCH** installed and running

## Step 1: Install Python Dependencies

```powershell
# Install the Ghana NLP Python library
pip install ghana-nlp

# Or install from requirements.txt
pip install -r requirements.txt
```

## Step 2: Get Your Ghana NLP API Key

1. Visit: https://translation.ghananlp.org/
2. Sign up for an account (if you don't have one)
3. Get your API key from the developer dashboard
4. Set it as an environment variable:

   **Windows (PowerShell):**
   ```powershell
   $env:GHANA_NLP_API_KEY = "your_api_key_here"
   ```

   **Windows (Command Prompt):**
   ```cmd
   set GHANA_NLP_API_KEY=your_api_key_here
   ```

   **Linux/Mac:**
   ```bash
   export GHANA_NLP_API_KEY="your_api_key_here"
   ```

## Step 3: Generate Twi Greeting Audio

Run the Python script to generate the Twi greeting:

```powershell
# With API key from environment variable
python generate_twi_greeting.py

# Or pass API key directly
python generate_twi_greeting.py --api-key "your_api_key_here"
```

This will:
- Convert the Twi text "Akwaaba. Yɛma wo akwaaba wɔ FreeSWITCH." to speech
- Save it as `sounds/custom/twi_greeting.wav`

### Custom Twi Text

You can modify the greeting text in `generate_twi_greeting.py`:

```python
# Change this line in the script:
twi_text = "Your custom Twi greeting here"
```

## Step 4: Copy Audio File to FreeSWITCH

### Windows:

```powershell
# Create custom sounds directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "C:\Program Files\FreeSWITCH\sounds\custom"

# Copy the generated file
Copy-Item -Path "sounds\custom\twi_greeting.wav" -Destination "C:\Program Files\FreeSWITCH\sounds\custom\twi_greeting.wav" -Force
```

### Linux:

```bash
# Create custom sounds directory
sudo mkdir -p /usr/share/freeswitch/sounds/en/us/callie/custom

# Copy the file
sudo cp sounds/custom/twi_greeting.wav /usr/share/freeswitch/sounds/en/us/callie/custom/twi_greeting.wav
```

## Step 5: Update FreeSWITCH Dialplan

The dialplan has already been updated to use the Twi greeting. Copy it to FreeSWITCH:

```powershell
# Windows
Copy-Item -Path "conf\dialplan\default.xml" -Destination "C:\Program Files\FreeSWITCH\conf\dialplan\default.xml" -Force
```

Then reload FreeSWITCH:

```powershell
fs_cli -x "reloadxml"
```

## Step 6: Test the Twi Greeting

1. Register your SIP client (MicroSIP/Linphone) with extension 1000
2. Dial **1001**
3. You should hear:
   - A short tone
   - **Twi greeting**: "Akwaaba. Yɛma wo akwaaba wɔ FreeSWITCH." (Welcome. We welcome you to FreeSWITCH.)
   - Call ends

## Troubleshooting

### "ghana-nlp package not installed"
```powershell
pip install ghana-nlp
```

### "Ghana NLP API key required"
- Make sure you've set the `GHANA_NLP_API_KEY` environment variable
- Or pass it with `--api-key` parameter
- Get your API key from: https://translation.ghananlp.org/

### "Failed to generate TTS"
- Check your internet connection
- Verify your API key is correct
- Ensure the Ghana NLP service is available
- Check API rate limits if you're making many requests

### "File not found" when calling
- Verify the audio file exists in the FreeSWITCH sounds directory
- Check the file path in the dialplan matches the actual location
- Ensure FreeSWITCH has read permissions on the file

### No audio plays
- Check FreeSWITCH logs: `fs_cli -x "console loglevel debug"`
- Verify the WAV file format is compatible (8kHz or 16kHz mono recommended)
- Test with a simple English WAV file first to verify audio playback works

## Customization

### Change the Greeting Text

Edit `generate_twi_greeting.py` and modify:

```python
twi_text = "Your custom Twi text here"
```

Then regenerate the audio file.

### Use Different Ghanaian Languages

The Ghana NLP API supports multiple languages:
- Twi: `lang="tw"`
- Ga: `lang="ga"`
- Ewe: `lang="ee"`
- And more...

Modify the script to use a different language code:

```python
audio_binary = nlp.text_to_speech(twi_text, lang="ga")  # For Ga language
```

### Generate Multiple Greetings

You can create multiple audio files for different scenarios:

```python
greetings = {
    "welcome": "Akwaaba. Yɛma wo akwaaba wɔ FreeSWITCH.",
    "goodbye": "Nante yie. Yɛbɛhyia bio.",
    "error": "Nsɛm bi ayɛ mmerɛw. Yɛsrɛ wo sɛ san bra bio."
}

for name, text in greetings.items():
    audio = nlp.text_to_speech(text, lang="tw")
    with open(f"sounds/custom/twi_{name}.wav", "wb") as f:
        f.write(audio)
```

## Advanced: Dynamic TTS (Future Enhancement)

For dynamic Twi TTS during calls (not pre-generated files), you would need to:

1. Create a FreeSWITCH ESL (Event Socket Library) application
2. Use the Ghana NLP API in real-time during the call
3. Stream the generated audio to FreeSWITCH

This is more complex and requires additional development work.

## Resources

- **Ghana NLP PyPI**: https://pypi.org/project/ghana-nlp/
- **Ghana NLP GitHub**: https://github.com/PhidLarkson/Ghana-NLP-Python-Library
- **Khaya AI API Portal**: https://translation.ghananlp.org/
- **TalkGhana Repository**: https://github.com/mintahandrews/talkghana
- **FreeSWITCH Documentation**: https://freeswitch.org/confluence/

## License

This integration uses the Ghana NLP API service. Please review their terms of service and API usage policies.
