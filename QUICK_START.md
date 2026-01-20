# Quick Start Guide

## Prerequisites Checklist
- [ ] FreeSWITCH installed and running
- [ ] Linphone installed
- [ ] Network connectivity between Linphone and FreeSWITCH

## Configuration Steps

### 1. FreeSWITCH Configuration (5 minutes)

```bash
# Navigate to FreeSWITCH config directory
cd /usr/local/freeswitch/conf  # Linux
# OR
cd "C:\Program Files\FreeSWITCH\conf"  # Windows

# Copy dialplan configuration
# (Copy conf/dialplan/default.xml to your dialplan directory)

# Copy directory configuration  
# (Copy conf/directory/default.xml to your directory directory)

# Reload configuration
fs_cli -x "reloadxml"
fs_cli -x "reload mod_sofia"
```

### 2. Linphone Configuration (2 minutes)

1. Open Linphone
2. Go to **Settings** → **SIP Accounts** → **Add**
3. Enter:
   - **Username**: `1000`
   - **Password**: `1234`
   - **Domain**: `localhost` (or FreeSWITCH IP address)
   - **Transport**: `UDP`
4. Save and verify registration status shows "Registered"

### 3. Test the Call (1 minute)

1. Open Linphone dialer
2. Dial: `1000`
3. Click **Call**
4. You should hear: "Hello, welcome to FreeSWITCH"

## Verification Commands

```bash
# Check FreeSWITCH status
fs_cli -x "status"

# Check registered users
fs_cli -x "sofia status"

# View dialplan
fs_cli -x "show dialplan default"

# Monitor logs (while making a call)
tail -f /usr/local/freeswitch/log/freeswitch.log
```

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Linphone won't register | Check FreeSWITCH is running, verify IP address and port 5060 |
| Call doesn't connect | Verify dialplan is loaded: `fs_cli -x "show dialplan default"` |
| No audio | Check codec support, verify firewall allows RTP ports (10000-20000) |
| Registration fails | Verify username (1000) and password (1234) are correct |

## Configuration Files Location

- **Dialplan**: `conf/dialplan/default.xml`
- **Directory**: `conf/directory/default.xml`

## Default Credentials

- **Extension**: `1000`
- **Password**: `1234`
- **Domain**: `localhost` (or your FreeSWITCH server IP)