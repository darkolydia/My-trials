# Voice-Assistant-Cultiflow

A call-based voice AI assistant that lets smartphone users interact with an intelligent system through phone calls. The system converts speech in a local language to text, understands user intent using an AI model, and responds with synthesized speech via a scalable FastAPI backend.

## FreeSWITCH Telephony System Configuration

This repository includes FreeSWITCH configuration files for setting up a SIP-based telephony system that can be used as the foundation for the voice assistant.

### System Overview

- **FreeSWITCH**: SIP server/PBX handling call routing
- **SIP Clients**: MicroSIP, Linphone, or any SIP-compatible softphone
- **Extensions**: 
  - Extension 1000: SIP user with greeting
  - Extension 1001: SIP user with greeting and tone

## Prerequisites

### For FreeSWITCH:
- Windows or Linux system
- FreeSWITCH installed and running
- Access to FreeSWITCH configuration directory (typically `C:\Program Files\FreeSWITCH\conf\` on Windows or `/usr/local/freeswitch/conf/` on Linux)

### For SIP Clients:
- MicroSIP, Linphone, or any SIP-compatible softphone installed
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

### 2. Install SIP Client

- **MicroSIP**: Download from https://www.microsip.org/
- **Linphone**: Download from https://www.linphone.org/
- **Android/iOS**: Install from respective app stores

## Configuration

### Step 1: Configure FreeSWITCH Dialplan

1. Navigate to your FreeSWITCH configuration directory:
   - Windows: `C:\Program Files\FreeSWITCH\conf\`
   - Linux: `/usr/local/freeswitch/conf/` or `/etc/freeswitch/`

2. **Copy the dialplan configuration:**
   ```powershell
   Copy-Item -Path "conf\dialplan\default.xml" -Destination "C:\Program Files\FreeSWITCH\conf\dialplan\default.xml" -Force
   ```

   The dialplan includes:
   - Extension 1000: Plays greeting with TTS
   - Extension 1001: Plays tone and greeting with TTS
   - SMS/MESSAGE handler: Logs incoming text messages

### Step 2: Configure SIP User Directory

1. **Copy the directory configuration:**
   ```powershell
   Copy-Item -Path "conf\directory\default.xml" -Destination "C:\Program Files\FreeSWITCH\conf\directory\default.xml" -Force
   ```

   The directory creates:
   - User 1000 with password 1234
   - User 1001 with password 1234
   - Domain set to your local IP (e.g., 10.255.1.104)

### Step 3: Configure Windows Firewall (Windows only)

Run the firewall setup script as Administrator:
```powershell
.\setup-firewall.ps1
```

Or manually configure firewall rules for:
- SIP UDP/TCP port 5060
- RTP UDP ports 10000-20000

### Step 4: Reload FreeSWITCH Configuration

After making configuration changes, reload FreeSWITCH:

#### Windows:
```powershell
fs_cli -x "reloadxml"
fs_cli -x "reload mod_sofia"
```

#### Linux:
```bash
fs_cli -x "reloadxml"
fs_cli -x "reload mod_sofia"
```

## SIP Client Configuration

### MicroSIP Configuration

1. Open MicroSIP
2. Go to **Account** → **Add Account**
3. Enter:
   - **User**: `1000` (or `1001`)
   - **Password**: `1234`
   - **Domain**: Your FreeSWITCH IP (e.g., `10.255.1.104`)
   - **Server**: Your FreeSWITCH IP (e.g., `10.255.1.104`)
   - **Port**: `5060`
   - **Transport**: `UDP`

### Linphone Configuration

1. Go to **Settings** → **SIP Accounts**
2. Click **Add** to create a new account
3. Enter:
   - **Username**: `1000`
   - **Password**: `1234`
   - **Domain/Server**: Your FreeSWITCH IP (e.g., `10.255.1.104`)
   - **Transport**: `UDP`
   - **Port**: `5060`

## Testing the System

### End-to-End Test Procedure

1. **Verify FreeSWITCH is running:**
   ```powershell
   fs_cli -x "status"
   ```

2. **Verify SIP user registration:**
   ```powershell
   fs_cli -x "sofia status profile internal reg"
   ```
   You should see your user (1000 or 1001) registered.

3. **Make a test call:**
   - In your SIP client, dial: `1001`
   - Press Call
   - You should hear:
     - A short tone
     - "Hello, welcome to FreeSWITCH" (spoken via TTS)
     - Then the call ends

4. **Monitor FreeSWITCH logs:**
   - Watch the FreeSWITCH Console window
   - Or enable debug logging: `fs_cli -x "console loglevel debug"`

### Expected Call Flow

1. SIP client initiates call to extension 1001
2. FreeSWITCH receives the INVITE request
3. FreeSWITCH matches extension 1001 in dialplan
4. FreeSWITCH answers the call
5. FreeSWITCH plays a tone
6. FreeSWITCH speaks greeting using TTS (Flite)
7. Call terminates normally

## Troubleshooting

### SIP Client Cannot Register:
- **Check FreeSWITCH is running**: `fs_cli -x "status"`
- **Verify SIP port is open**: Check firewall rules
- **Check firewall settings**: Ensure UDP/TCP port 5060 is not blocked
- **Verify credentials**: Username and password match directory configuration
- **Check domain**: Use actual IP address, not `localhost` or `127.0.0.1`
- **Check FreeSWITCH logs**: Look for SIP registration errors

### Call Does Not Connect:
- **Verify dialplan is loaded**: `fs_cli -x "xml_locate dialplan default"`
- **Check extension exists**: `fs_cli -x "show dialplan default"`
- **Monitor call in real-time**: `fs_cli -x "console loglevel debug"` then make call
- **Verify user is registered**: `fs_cli -x "sofia status profile internal reg"`
- **Check ACL settings**: Ensure `apply-inbound-acl` is set to `none` in `internal.xml` for testing

### No Audio/Greeting:
- **Check TTS module**: `fs_cli -x "module_exists mod_flite"` (should return `true`)
- **Load TTS module**: `fs_cli -x "load mod_flite"` if not loaded
- **Check audio codecs**: Ensure FreeSWITCH and SIP client support common codecs (PCMU, PCMA)
- **Verify RTP ports**: Ensure firewall allows RTP ports 10000-20000

### Network Issues:
- **Same machine**: Use actual IP address, not `localhost`
- **Different machines**: Use actual IP address of FreeSWITCH server
- **Firewall**: Ensure SIP (5060) and RTP (10000-20000) ports are open
- **NAT**: Check `conf/sip_profiles/internal.xml` for NAT-related settings

## Configuration Files Reference

### Dialplan Configuration (`conf/dialplan/default.xml`)
- Defines call routing rules
- Extension 1000: Answers and plays greeting
- Extension 1001: Answers, plays tone, and speaks greeting
- SMS handler: Logs incoming MESSAGE requests
- Uses TTS (Text-to-Speech) via Flite module

### Directory Configuration (`conf/directory/default.xml`)
- Defines SIP users/extensions
- User 1000 with password 1234
- User 1001 with password 1234
- Sets caller ID and other user variables
- Domain explicitly set to local IP

### SIP Profile Configuration (`conf/sip_profiles/internal.xml`)
- Configures internal SIP profile
- Context set to `default`
- Authentication and ACL settings
- NAT handling configuration

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

### Twi (Ghanaian Language) Greeting Integration

This repository includes **Ghana NLP integration** for Twi greetings! Extension 1001 now plays a greeting in Twi instead of English.

**Quick Setup:**

1. **Get Ghana NLP API Key**: Sign up at https://translation.ghananlp.org/
2. **Install Python dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
3. **Run the setup script**:
   ```powershell
   # Set your API key
   $env:GHANA_NLP_API_KEY = "your_api_key_here"
   
   # Run setup
   .\setup-twi-greeting.ps1
   ```

This will:
- Generate a Twi greeting audio file using Ghana NLP TTS
- Copy it to FreeSWITCH sounds directory
- Update the dialplan to use the Twi greeting
- Reload FreeSWITCH configuration

**Manual Setup:** See [GHANA_NLP_SETUP.md](GHANA_NLP_SETUP.md) for detailed instructions.

**Test:** Dial 1001 from your SIP client to hear: "Akwaaba. Yɛma wo akwaaba wɔ FreeSWITCH." (Welcome. We welcome you to FreeSWITCH.)

### Other Local Languages
To use other local languages:
1. Record or generate a WAV file in the desired language
2. Place it in FreeSWITCH sounds directory
3. Update dialplan to use `playback` instead of `speak`:
   ```xml
   <action application="playback" data="custom/your_greeting.wav"/>
   ```

## Security Notes

- **Default password is weak**: Change password `1234` in production
- **Network security**: Consider using VPN or firewall rules for production deployments
- **TLS/SRTP**: For secure communications, configure TLS and SRTP in FreeSWITCH and SIP clients
- **ACL**: Re-enable and properly configure ACLs for production use

## Additional Resources

- FreeSWITCH Documentation: https://freeswitch.org/confluence/
- MicroSIP Documentation: https://www.microsip.org/
- Linphone Documentation: https://wiki.linphone.org/
- FreeSWITCH Mailing List: https://lists.freeswitch.org/

## License

This configuration is provided as-is for educational and testing purposes.
