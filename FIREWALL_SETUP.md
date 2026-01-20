# Windows Firewall Setup for FreeSWITCH

## Quick Fix: Run PowerShell Script (Easiest Method)

1. **Right-click on PowerShell** (or Command Prompt) and select **"Run as Administrator"**

2. **Navigate to this directory:**
   ```powershell
   cd "C:\Users\User\Desktop\FreeSWITCH-to-linphone"
   ```

3. **Run the firewall script:**
   ```powershell
   .\setup-firewall.ps1
   ```

## Manual Method: Using Windows Firewall GUI

### Step 1: Open Windows Defender Firewall
1. Press `Windows key + R`
2. Type `wf.msc` and press Enter
3. Click **"Inbound Rules"** in the left panel
4. Click **"New Rule..."** in the right panel

### Step 2: Add UDP Rule for Port 5060
1. Select **"Port"** → Next
2. Select **"UDP"** → Next
3. Select **"Specific local ports"** → Enter: `5060` → Next
4. Select **"Allow the connection"** → Next
5. Check all profiles (Domain, Private, Public) → Next
6. Name: `FreeSWITCH SIP UDP 5060` → Finish

### Step 3: Add TCP Rule for Port 5060
Repeat Step 2, but select **"TCP"** instead of UDP, and name it `FreeSWITCH SIP TCP 5060`

### Step 4: Add UDP Rule for RTP Ports (10000-20000)
Repeat Step 2, but:
- Select **"UDP"**
- Enter ports: `10000-20000`
- Name: `FreeSWITCH RTP 10000-20000`

## Manual Method: Using Command Line (Run as Admin)

Open PowerShell **as Administrator** and run:

```powershell
# Allow SIP UDP 5060
New-NetFirewallRule -DisplayName "FreeSWITCH SIP UDP 5060" `
    -Direction Inbound -Protocol UDP -LocalPort 5060 -Action Allow

# Allow SIP TCP 5060
New-NetFirewallRule -DisplayName "FreeSWITCH SIP TCP 5060" `
    -Direction Inbound -Protocol TCP -LocalPort 5060 -Action Allow

# Allow RTP ports (10000-20000)
New-NetFirewallRule -DisplayName "FreeSWITCH RTP 10000-20000" `
    -Direction Inbound -Protocol UDP -LocalPort 10000-20000 -Action Allow
```

## Verify Firewall Rules

After adding rules, verify they exist:

```powershell
# List FreeSWITCH firewall rules
Get-NetFirewallRule -DisplayName "*FreeSWITCH*" | Format-Table DisplayName, Enabled, Direction, Action
```

## Check if Port 5060 is Listening

```powershell
netstat -an | Select-String "5060"
```

You should see:
```
TCP    0.0.0.0:5060           0.0.0.0:0              LISTENING
UDP    0.0.0.0:5060           *:*
```

## Important Notes

- **SIP Port 5060**: Required for SIP signaling (call setup)
- **RTP Ports 10000-20000**: Required for audio/video media (actual call audio)
- If you're on the **same machine** (localhost), firewall may not be an issue
- If Linphone is on a **different machine**, firewall rules are essential
- **Restart FreeSWITCH** after adding firewall rules if needed

## Troubleshooting

### If rules still don't work:
1. Make sure you ran PowerShell **as Administrator**
2. Check Windows Firewall is enabled: `Get-NetFirewallProfile | Select-Object Name, Enabled`
3. Try temporarily disabling firewall to test: `Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False` (re-enable after testing!)
4. Check if Windows Defender or third-party firewall is also blocking

## Test Connection

After adding firewall rules:
1. Register Linphone with FreeSWITCH
2. Check registration: `fs_cli -x "sofia status profile internal reg"`
3. Make a test call to extension 1000
