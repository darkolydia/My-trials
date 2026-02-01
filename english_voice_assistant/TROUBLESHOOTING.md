# Troubleshooting Guide - English Voice Assistant

## Password Issues

### Wrong Password Error

If you're getting a "password is wrong" error in MicroSIP:

**Correct Credentials:**
- **Username**: `1000`
- **Password**: `1234`
- **Domain**: `10.255.1.104` (or your FreeSWITCH IP)
- **SIP Server**: `10.255.1.104` (or your FreeSWITCH IP)
- **Port**: `5060`
- **Transport**: `UDP`

**Steps to Fix:**

1. **Verify directory configuration is loaded:**
   ```powershell
   fs_cli -x "reloadxml"
   fs_cli -x "reload mod_directory"
   ```

2. **Check if user exists:**
   ```powershell
   fs_cli -x "user_exists id 1000 domain 10.255.1.104"
   ```
   Should return `true`

3. **Copy directory config if needed:**
   ```powershell
   Copy-Item -Path "C:\Users\User\Desktop\FreeSWITCH-to-linphone\conf\directory\default.xml" -Destination "C:\Program Files\FreeSWITCH\conf\directory\default.xml" -Force
   fs_cli -x "reloadxml"
   ```

4. **In MicroSIP, double-check:**
   - Username: `1000` (not `1000@10.255.1.104`)
   - Password: `1234` (exactly, no spaces)
   - Domain: `10.255.1.104`
   - SIP Server: `10.255.1.104`

5. **Check FreeSWITCH logs:**
   ```powershell
   fs_cli -x "console loglevel debug"
   ```
   Then try registering again and watch for authentication errors

## Registration Issues

### Cannot Register

**Check FreeSWITCH is running:**
```powershell
fs_cli -x "status"
```

**Check SIP profile status:**
```powershell
fs_cli -x "sofia status"
fs_cli -x "sofia status profile internal"
```

**Check if user is registered:**
```powershell
fs_cli -x "sofia status profile internal reg"
```

**Verify SIP port is open:**
- Check Windows Firewall allows port 5060 (UDP/TCP)
- Check if another application is using port 5060

## Call Issues

### Extension 1003 Not Working

**Check dialplan is loaded:**
```powershell
fs_cli -x "show dialplan default" | findstr 1003
```

**Check dialplan file:**
```powershell
Get-Content "C:\Program Files\FreeSWITCH\conf\dialplan\default.xml" | Select-String "1003"
```

**Reload dialplan:**
```powershell
fs_cli -x "reloadxml"
```

**Monitor call in real-time:**
```powershell
fs_cli -x "console loglevel debug"
```
Then make a call and watch the logs

## Audio Issues

### No Audio During Call

**Check audio codecs:**
```powershell
fs_cli -x "show codecs"
```

**Verify RTP ports are open:**
- Windows Firewall should allow UDP ports 10000-20000

**Check audio path:**
- Make sure microphone is working in MicroSIP
- Check MicroSIP audio settings

### No Response Audio

**Check if response file was created:**
```powershell
Test-Path "C:\Program Files\FreeSWITCH\sounds\custom\response_english.wav"
```

**Check Python script ran successfully:**
- Look at FreeSWITCH logs for Python errors
- Test script manually:
  ```powershell
  python "C:\Users\User\Desktop\FreeSWITCH-to-linphone\english_voice_assistant\voice_assistant.py" --text "hello"
  ```

**Check recording was created:**
```powershell
Test-Path "C:\Users\User\Desktop\Recordings\user_question_english.wav"
```

## Python Script Issues

### Script Not Found

**Verify path is correct:**
```powershell
Test-Path "C:\Users\User\Desktop\FreeSWITCH-to-linphone\english_voice_assistant\voice_assistant.py"
```

**Check Python is in PATH:**
```powershell
python --version
```

### API Key Error

**Check .env file exists:**
```powershell
Test-Path "C:\Users\User\Desktop\FreeSWITCH-to-linphone\english_voice_assistant\.env"
Get-Content "C:\Users\User\Desktop\FreeSWITCH-to-linphone\english_voice_assistant\.env"
```

### TTS Failed

**Check dependencies:**
```powershell
pip install -r "C:\Users\User\Desktop\FreeSWITCH-to-linphone\english_voice_assistant\requirements.txt"
```

**Test TTS manually:**
```powershell
python "C:\Users\User\Desktop\FreeSWITCH-to-linphone\english_voice_assistant\voice_assistant.py" --text "test"
```

## Common Solutions

### Reset Everything

1. **Reload FreeSWITCH:**
   ```powershell
   fs_cli -x "reloadxml"
   fs_cli -x "reload mod_sofia"
   fs_cli -x "reload mod_directory"
   ```

2. **Restart FreeSWITCH service** (if running as service):
   ```powershell
   Restart-Service freeswitch
   ```

3. **Delete and recreate MicroSIP account:**
   - Delete account in MicroSIP
   - Create new account with correct credentials
   - Register again

### Verify Configuration Files

**Check all config files are in place:**
```powershell
# Dialplan
Test-Path "C:\Program Files\FreeSWITCH\conf\dialplan\default.xml"

# Directory
Test-Path "C:\Program Files\FreeSWITCH\conf\directory\default.xml"

# SIP Profile (should exist)
Test-Path "C:\Program Files\FreeSWITCH\conf\sip_profiles\internal.xml"
```

**Copy configs if missing:**
```powershell
Copy-Item -Path "C:\Users\User\Desktop\FreeSWITCH-to-linphone\conf\*" -Destination "C:\Program Files\FreeSWITCH\conf\" -Recurse -Force
fs_cli -x "reloadxml"
```

## Getting Help

**Check logs:**
- FreeSWITCH logs: `C:\Program Files\FreeSWITCH\log\freeswitch.log`
- Last call log: `C:\Users\User\Desktop\Recordings\last_call_log.txt`
- Live log: `C:\Users\User\Desktop\Recordings\live_log.txt`

**Test components individually:**
1. Test FreeSWITCH: `fs_cli -x "status"`
2. Test SIP registration: `fs_cli -x "sofia status profile internal reg"`
3. Test dialplan: `fs_cli -x "show dialplan default"`
4. Test Python script: `python voice_assistant.py --text "hello"`
5. Test audio recording manually
