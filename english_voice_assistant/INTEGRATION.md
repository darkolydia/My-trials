# FreeSWITCH Integration Guide

This guide explains how to integrate the English Voice Assistant with FreeSWITCH so you can call it from MicroSIP.

## Quick Setup

1. **Run the setup script:**
   ```powershell
   cd english_voice_assistant
   .\setup_freeswitch.ps1
   ```

2. **Reload FreeSWITCH dialplan:**
   ```powershell
   fs_cli -x "reloadxml"
   ```

3. **Call extension 1003 from MicroSIP**

## Manual Setup

### Step 1: Update FreeSWITCH Dialplan

The dialplan has been updated to include extension **1003** for the English Voice Assistant.

**Extension 1003 Flow:**
1. Answers the call
2. Plays a greeting: "Hello! I am your English voice assistant. Please ask me a question."
3. Records your question (up to 20 seconds)
4. Processes the question using the English voice assistant
5. Plays the response
6. Hangs up

### Step 2: Copy Dialplan to FreeSWITCH

```powershell
Copy-Item -Path "conf\dialplan\default.xml" -Destination "C:\Program Files\FreeSWITCH\conf\dialplan\default.xml" -Force
```

### Step 3: Reload FreeSWITCH

```powershell
fs_cli -x "reloadxml"
```

## Testing

### From MicroSIP:

1. **Register your account** (if not already registered):
   - User: `1000`
   - Password: `1234`
   - Domain: Your FreeSWITCH IP (e.g., `10.255.1.104`)
   - Port: `5060`

2. **Dial extension 1003**

3. **When you hear the greeting**, speak your question in English

4. **Wait for the response** - the system will:
   - Process your question
   - Match it to a Q&A pair
   - Generate English speech
   - Play the answer

## Extension Numbers

| Extension | Description |
|-----------|-------------|
| 1000 | Simple greeting (English) |
| 1001 | Twi greeting |
| 1002 | Twi Voice Assistant (with database) |
| **1003** | **English Voice Assistant (hardcoded Q&A)** |

## File Paths

The dialplan uses these paths:

- **Voice Assistant Script**: `C:\Users\User\Desktop\FreeSWITCH-to-linphone\english_voice_assistant\voice_assistant.py`
- **Recording Input**: `C:\Users\User\Desktop\Recordings\user_question_english.wav`
- **Response Output**: `C:\Program Files\FreeSWITCH\sounds\custom\response_english.wav`

## Troubleshooting

### Call doesn't connect:
- Check FreeSWITCH is running: `fs_cli -x "status"`
- Verify extension 1003 exists: `fs_cli -x "show dialplan default" | findstr 1003`
- Check MicroSIP is registered: `fs_cli -x "sofia status profile internal reg"`

### No audio/response:
- Check FreeSWITCH logs: `fs_cli -x "console loglevel debug"`
- Verify Python script path is correct
- Check response file exists: `C:\Program Files\FreeSWITCH\sounds\custom\response_english.wav`
- Test script manually: `python voice_assistant.py --text "hello"`

### Recording issues:
- Check recording directory exists: `C:\Users\User\Desktop\Recordings`
- Verify permissions on recording directory
- Check FreeSWITCH can write to the directory

### Processing fails:
- Check Python dependencies: `pip install -r requirements.txt`
- Verify API key in `.env` file
- Test script manually with audio file

## Monitoring

### Watch FreeSWITCH logs:
```powershell
# In FreeSWITCH console or fs_cli
console loglevel debug
```

### Check last question/answer:
```powershell
# View the log file
Get-Content "C:\Users\User\Desktop\Recordings\last_question.txt"
```

### View live log:
```powershell
Get-Content "C:\Users\User\Desktop\Recordings\live_log.txt" -Wait
```

## Next Steps

1. **Add more Q&A pairs** - Edit `voice_assistant.py` and add to `QA_PAIRS` dictionary
2. **Customize greeting** - Modify the dialplan greeting message
3. **Add multiple question loops** - Modify dialplan to allow multiple questions per call
4. **Improve error handling** - Add fallback messages for failed processing
