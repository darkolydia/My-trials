# Copy Twi greeting (and please-wait) to FreeSWITCH sounds directory.
# Run from project root. Generate first: python generate_twi_greeting.py

$ErrorActionPreference = "Stop"
$Dest = "C:\Program Files\FreeSWITCH\sounds\custom"

if (-not (Test-Path $Dest)) {
    Write-Host "Creating $Dest"
    New-Item -ItemType Directory -Force -Path $Dest | Out-Null
}

$copied = $false
if (Test-Path "sounds\custom\twi_greeting.wav") {
    Copy-Item -Path "sounds\custom\twi_greeting.wav" -Destination "$Dest\twi_greeting.wav" -Force
    Write-Host "Copied twi_greeting.wav to FreeSWITCH"
    $copied = $true
} else {
    Write-Host "WARN: sounds\custom\twi_greeting.wav not found. Run: python generate_twi_greeting.py"
}

if (Test-Path "sounds\custom\twi_please_wait.wav") {
    Copy-Item -Path "sounds\custom\twi_please_wait.wav" -Destination "$Dest\twi_please_wait.wav" -Force
    Write-Host "Copied twi_please_wait.wav to FreeSWITCH"
    $copied = $true
}

if (-not $copied) {
    Write-Host "No files copied. Generate greeting first: python generate_twi_greeting.py"
    exit 1
}

Write-Host "Done. Reload FreeSWITCH: fs_cli -x reloadxml"
