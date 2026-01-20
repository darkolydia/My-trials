# FreeSWITCH Firewall Configuration Script
# Run this script as Administrator

Write-Host "Configuring Windows Firewall for FreeSWITCH..." -ForegroundColor Green

# Allow SIP UDP port 5060
Write-Host "Adding firewall rule for SIP UDP 5060..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "FreeSWITCH SIP UDP 5060" `
    -Direction Inbound `
    -Protocol UDP `
    -LocalPort 5060 `
    -Action Allow `
    -Profile Any `
    -ErrorAction SilentlyContinue

# Allow SIP TCP port 5060
Write-Host "Adding firewall rule for SIP TCP 5060..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "FreeSWITCH SIP TCP 5060" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 5060 `
    -Action Allow `
    -Profile Any `
    -ErrorAction SilentlyContinue

# Allow RTP port range (typically 10000-20000 for audio/video)
Write-Host "Adding firewall rule for RTP ports 10000-20000..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "FreeSWITCH RTP 10000-20000" `
    -Direction Inbound `
    -Protocol UDP `
    -LocalPort 10000-20000 `
    -Action Allow `
    -Profile Any `
    -ErrorAction SilentlyContinue

Write-Host "`nFirewall rules added successfully!" -ForegroundColor Green
Write-Host "Verifying rules..." -ForegroundColor Yellow

# Verify the rules
Get-NetFirewallRule -DisplayName "*FreeSWITCH*" | Format-Table DisplayName, Enabled, Direction, Action

Write-Host "`nFirewall configuration complete!" -ForegroundColor Green
