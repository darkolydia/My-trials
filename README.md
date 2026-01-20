# FreeSWITCH to Linphone Telephony System

A simple telephony system where Linphone acts as a SIP client connecting to FreeSWITCH, which answers calls to extension 1000 and plays a greeting message.

## System Overview

- **FreeSWITCH**: SIP server/PBX handling call routing
- **Linphone**: SIP client softphone for making calls
- **Extension 1000**: SIP user that can receive calls with a greeting

## Prerequisites

### For FreeSWITCH:
- Windows or Linux system
- FreeSWITCH installed and running
- Access to FreeSWITCH configuration directory (typically `C:\Program Files\FreeSWITCH\conf\` on Windows or `/usr/local/freeswitch/conf/` on Linux)

### For Linphone:
- Linphone application installed (available for Windows, Linux, macOS, Android, iOS)
- Network connectivity to the FreeSWITCH server

## Installation

### 1. Install FreeSWITCH

#### Windows:
1. Download FreeSWITCH installer from: https://freeswitch.org/confluence/display/FREESWITCH/Installation
2. Run the installer and follow the installation wizard
3. FreeSWITCH typically installs to: `C:\Program Files\FreeSWITCH\`

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install -y freeswitch freeswitch-mod-commands freeswitch-mod-dptools freeswitch-mod-flite
```

#### Linux (CentOS/RHEL):
```bash
# Add EPEL repository first
sudo yum install -y epel-release
sudo yum install -y freeswitch
```

### 2. Install Linphone

- **Windows/Linux**: Download from https://www.linphone.org/
- **Android/iOS**: Install from respective app stores
- **macOS**: Download from https://www.linphone.org/

## Configuration

### Step 1: Configure FreeSWITCH Dialplan

1. Navigate to your FreeSWITCH configuration directory:
   - Windows: `C:\Program Files\FreeSWITCH\conf\`
   - Linux: `/usr/local/freeswitch/conf/` or `/etc/freeswitch/`

2. **Copy or merge the dialplan configuration:**
   - Copy `conf/dialplan/default.xml` from this repository
   - Or merge the extension 1000 configuration into your existing `conf/dialplan/default.xml`

   The dialplan entry for extension 1000:
   ```xml
   <extension name="extension_1000">
     <condition field="destination_number" expression="^1000$">
       <action application="answer"/>
       <action application="sleep" data="1000"/>
       <action application="playback" data="ivr/ivr-hello.wav"/>
       <action application="speak" data="flite|kal|Hello, welcome to FreeSWITCH"/>
       <action application="hangup" data="NORMAL_CLEARING"/>
     </condition>
   </extension>
   ```

### Step 2: Configure SIP User Directory

1. **Copy or merge the directory configuration:**
   - Copy `conf/directory/default.xml` from this repository
   - Or merge the user 1000 configuration into your existing `conf/directory/default.xml`

   The directory entry creates user 1000 with password 1234:
   ```xml
   <user id="1000">
     <params>
       <param name="password" value="1234"/>
       <param name="vm-password" value="1000"/>
     </params>
     <variables>
       <variable name="effective_caller_id_name" value="Extension 1000"/>
       <variable name="effective_caller_id_number" value="1000"/>
       ...
     </variables>
   </user>
   ```

### Step 3: Reload FreeSWITCH Configuration

After making configuration changes, reload FreeSWITCH:

#### Windows:
- Use FreeSWITCH command line or service manager to reload:
  ```
  fs_cli -x "reload mod_xml_curl"
  fs_cli -x "reloadxml"
  ```

#### Linux:
```bash
# Connect to FreeSWITCH CLI
fs_cli

# Or reload directly:
fs_cli -x "reloadxml"
fs_cli -x "reload mod_sofia"
```

## Linphone Configuration

### Step 1: Launch Linphone

Open the Linphone application on your device.

### Step 2: Create SIP Account

1. Go to **Settings** → **SIP Accounts** (or **Accounts**)
2. Click **Add** or **+** to create a new account
3. Enter the following information:
   - **Username**: `1000`
   - **Password**: `1234`
   - **Domain/Server**: `localhost` (if Linphone is on the same machine) or the IP address of your FreeSWITCH server
   - **Transport**: `UDP` (or `TCP` if preferred)
   - **Port**: `5060` (default SIP port)

### Step 3: Register the Account

1. After entering the credentials, Linphone should automatically attempt to register
2. Check the status indicator - it should show **Registered** (green/green dot)
3. If registration fails, verify:
   - FreeSWITCH is running
   - Network connectivity to FreeSWITCH server
   - Firewall allows UDP/TCP port 5060
   - Username and password are correct

## Testing the System

### End-to-End Test Procedure

1. **Verify FreeSWITCH is running:**
   ```bash
   # Check FreeSWITCH status
   fs_cli -x "status"
   ```
   Should show FreeSWITCH is ready and running.

2. **Verify SIP user registration:**
   ```bash
   fs_cli -x "sofia status"
   ```
   You should see user 1000 registered in the output.

3. **Make a test call from Linphone:**
   - In Linphone, go to the **Dialer** tab
   - Enter the number: `1000`
   - Click **Call** or press Enter
   - The call should connect and you should hear: "Hello, welcome to FreeSWITCH"

4. **Monitor FreeSWITCH logs (optional):**
   ```bash
   # View real-time logs
   tail -f /usr/local/freeswitch/log/freeswitch.log
   # Or on Windows: check the log file in FreeSWITCH installation directory
   ```

### Expected Call Flow

1. Linphone initiates call to extension 1000
2. FreeSWITCH receives the INVITE request
3. FreeSWITCH matches extension 1000 in dialplan
4. FreeSWITCH answers the call
5. FreeSWITCH plays a greeting (WAV file if available, or TTS)
6. Call terminates normally

### Troubleshooting

#### Linphone Cannot Register:
- **Check FreeSWITCH is running**: `fs_cli -x "status"`
- **Verify SIP port is open**: `netstat -an | grep 5060`
- **Check firewall settings**: Ensure UDP/TCP port 5060 is not blocked
- **Verify credentials**: Username `1000`, Password `1234`
- **Check FreeSWITCH logs**: Look for SIP registration errors

#### Call Does Not Connect:
- **Verify dialplan is loaded**: `fs_cli -x "xml_locate dialplan default"`
- **Check extension exists**: `fs_cli -x "show dialplan default"`
- **Monitor call in real-time**: `fs_cli -x "console loglevel debug"` then make call
- **Verify user is registered**: `fs_cli -x "sofia status"`

#### No Audio/Greeting:
- **Check audio codecs**: Ensure FreeSWITCH and Linphone support common codecs (PCMU, PCMA)
- **Verify playback file exists**: If using WAV file, ensure it's in the correct path
- **TTS fallback**: The dialplan uses TTS as fallback if WAV file is missing

#### Network Issues:
- **Same machine**: Use `localhost` or `127.0.0.1` as domain
- **Different machines**: Use actual IP address of FreeSWITCH server
- **Firewall**: Ensure SIP (5060) and RTP (10000-20000 typically) ports are open

## Configuration Files Reference

### Dialplan Configuration (`conf/dialplan/default.xml`)
- Defines call routing rules
- Extension 1000 answers and plays greeting
- Uses TTS (Text-to-Speech) via Flite module

### Directory Configuration (`conf/directory/default.xml`)
- Defines SIP users/extensions
- User 1000 with password 1234
- Sets caller ID and other user variables

## Advanced Configuration

### Change SIP Port
Edit `conf/sip_profiles/internal.xml`:
```xml
<param name="sip-port" value="5060"/>
```

### Add More Extensions
Add additional `<user>` entries in `conf/directory/default.xml` and corresponding `<extension>` entries in `conf/dialplan/default.xml`.

### Custom Greeting Audio File
1. Place your WAV file in `sounds/` directory
2. Update dialplan: `<action application="playback" data="path/to/your/greeting.wav"/>`

## Security Notes

- **Default password is weak**: Change password `1234` in production
- **Network security**: Consider using VPN or firewall rules for production deployments
- **TLS/SRTP**: For secure communications, configure TLS and SRTP in FreeSWITCH and Linphone

## Additional Resources

- FreeSWITCH Documentation: https://freeswitch.org/confluence/
- Linphone Documentation: https://wiki.linphone.org/
- FreeSWITCH Mailing List: https://lists.freeswitch.org/

## License

This configuration is provided as-is for educational and testing purposes.