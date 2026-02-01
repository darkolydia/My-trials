# Test SIP Registration Script
# This helps diagnose SIP registration issues

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SIP Registration Diagnostic Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check FreeSWITCH is running
Write-Host "1. Checking FreeSWITCH status..." -ForegroundColor Yellow
$status = fs_cli -x "status" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ FreeSWITCH is running" -ForegroundColor Green
} else {
    Write-Host "   ✗ FreeSWITCH is not running!" -ForegroundColor Red
    exit 1
}

# Check SIP profile status
Write-Host ""
Write-Host "2. Checking SIP profile status..." -ForegroundColor Yellow
$sofiaStatus = fs_cli -x "sofia status profile internal" 2>&1
if ($sofiaStatus -match "RUNNING") {
    Write-Host "   ✓ SIP profile 'internal' is running" -ForegroundColor Green
} else {
    Write-Host "   ✗ SIP profile 'internal' is not running!" -ForegroundColor Red
    Write-Host "   Status: $sofiaStatus" -ForegroundColor Yellow
}

# Check directory config
Write-Host ""
Write-Host "3. Checking directory configuration..." -ForegroundColor Yellow
$dirFile = "C:\Program Files\FreeSWITCH\conf\directory\default.xml"
if (Test-Path $dirFile) {
    Write-Host "   ✓ Directory config file exists" -ForegroundColor Green
    $content = Get-Content $dirFile -Raw
    if ($content -match 'password.*value="(\d+)"') {
        $password = $matches[1]
        Write-Host "   ✓ Password found in config: $password" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Password not found in config!" -ForegroundColor Red
    }
} else {
    Write-Host "   ✗ Directory config file not found!" -ForegroundColor Red
}

# Check current registrations
Write-Host ""
Write-Host "4. Checking current registrations..." -ForegroundColor Yellow
$regs = fs_cli -x "sofia status profile internal reg" 2>&1
if ($regs -match "Total items returned: 0") {
    Write-Host "   ⚠ No users currently registered" -ForegroundColor Yellow
} else {
    Write-Host "   ✓ Registered users found:" -ForegroundColor Green
    Write-Host "   $regs" -ForegroundColor Gray
}

# Check if user exists
Write-Host ""
Write-Host "5. Checking if user 1000 exists..." -ForegroundColor Yellow
$userExists = fs_cli -x "user_exists id 1000 domain 10.255.1.104" 2>&1
if ($userExists -match "true") {
    Write-Host "   ✓ User 1000 exists in domain 10.255.1.104" -ForegroundColor Green
} else {
    Write-Host "   ✗ User 1000 does not exist!" -ForegroundColor Red
    Write-Host "   Response: $userExists" -ForegroundColor Yellow
}

# Reload configuration
Write-Host ""
Write-Host "6. Reloading FreeSWITCH configuration..." -ForegroundColor Yellow
$reload = fs_cli -x "reloadxml" 2>&1
if ($reload -match "Success") {
    Write-Host "   ✓ Configuration reloaded successfully" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Reload response: $reload" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MicroSIP Configuration Checklist:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Make sure these settings are EXACTLY:" -ForegroundColor Yellow
Write-Host "  Username: 1000" -ForegroundColor White
Write-Host "  Password: 1234" -ForegroundColor White
Write-Host "  Domain: 10.255.1.104" -ForegroundColor White
Write-Host "  SIP Server: 10.255.1.104" -ForegroundColor White
Write-Host "  Port: 5060" -ForegroundColor White
Write-Host "  Transport: UDP" -ForegroundColor White
Write-Host ""
Write-Host "Common Issues:" -ForegroundColor Yellow
Write-Host "  - Extra spaces in password field" -ForegroundColor White
Write-Host "  - Username should be '1000' not '1000@10.255.1.104'" -ForegroundColor White
Write-Host "  - Domain and SIP Server must match exactly" -ForegroundColor White
Write-Host "  - Make sure no firewall is blocking port 5060" -ForegroundColor White
Write-Host ""
Write-Host "After configuring MicroSIP, wait 5-10 seconds for registration." -ForegroundColor Cyan
Write-Host "Then check registration with:" -ForegroundColor Cyan
Write-Host '  fs_cli -x "sofia status profile internal reg"' -ForegroundColor Gray
Write-Host ""
