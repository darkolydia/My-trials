# Setup script for English Voice Assistant with FreeSWITCH
# This script helps configure FreeSWITCH to use the English voice assistant

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "English Voice Assistant - FreeSWITCH Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$freeswitchConfDir = "C:\Program Files\FreeSWITCH\conf"
$dialplanFile = "$freeswitchConfDir\dialplan\default.xml"
$projectRoot = Split-Path -Parent $PSScriptRoot
$dialplanSource = "$projectRoot\conf\dialplan\default.xml"

# Check if FreeSWITCH is installed
if (-not (Test-Path $freeswitchConfDir)) {
    Write-Host "✗ FreeSWITCH not found at: $freeswitchConfDir" -ForegroundColor Red
    Write-Host "Please install FreeSWITCH first" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ FreeSWITCH found" -ForegroundColor Green

# Check if dialplan source exists
if (-not (Test-Path $dialplanSource)) {
    Write-Host "✗ Dialplan source not found: $dialplanSource" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Dialplan source found" -ForegroundColor Green

# Backup existing dialplan
$backupFile = "$dialplanFile.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
if (Test-Path $dialplanFile) {
    Write-Host "Creating backup: $backupFile" -ForegroundColor Yellow
    Copy-Item $dialplanFile $backupFile -Force
    Write-Host "✓ Backup created" -ForegroundColor Green
}

# Copy dialplan
Write-Host ""
Write-Host "Copying dialplan..." -ForegroundColor Yellow
try {
    Copy-Item $dialplanSource $dialplanFile -Force
    Write-Host "✓ Dialplan copied successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to copy dialplan: $_" -ForegroundColor Red
    exit 1
}

# Create sounds directory if needed
$soundsDir = "C:\Program Files\FreeSWITCH\sounds\custom"
if (-not (Test-Path $soundsDir)) {
    Write-Host "Creating sounds directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $soundsDir -Force | Out-Null
    Write-Host "✓ Sounds directory created" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Reload FreeSWITCH dialplan:" -ForegroundColor White
Write-Host "   fs_cli -x `"reloadxml`"" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Test the English voice assistant:" -ForegroundColor White
Write-Host "   - Dial extension 1003 from MicroSIP" -ForegroundColor Gray
Write-Host "   - Speak your question in English" -ForegroundColor Gray
Write-Host "   - Listen to the response" -ForegroundColor Gray
Write-Host ""
Write-Host "Extension 1003: English Voice Assistant" -ForegroundColor Yellow
Write-Host "Extension 1002: Twi Voice Assistant (original)" -ForegroundColor Yellow
Write-Host ""
