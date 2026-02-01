# Setup script for Twi greeting integration with Ghana NLP
# This script helps set up the Twi greeting for FreeSWITCH

param(
    [string]$ApiKey = $null,
    [string]$FreeSwitchSoundsPath = "C:\Program Files\FreeSWITCH\sounds\custom"
)

# Try to load API key from .env file if not provided
if (-not $ApiKey) {
    $ApiKey = $env:GHANA_NLP_API_KEY
    if (-not $ApiKey) {
        $ApiKey = $env:GHANANLP_API_KEY
    }
    # If still not found, try reading from .env file
    if (-not $ApiKey -and (Test-Path ".env")) {
        $envContent = Get-Content ".env" | Where-Object { $_ -match "^GHANANLP_API_KEY=|^GHANA_NLP_API_KEY=" }
        if ($envContent) {
            $ApiKey = ($envContent -split "=", 2)[1].Trim()
        }
    }
}

Write-Host "=== Twi Greeting Setup for FreeSWITCH ===" -ForegroundColor Green
Write-Host ""

# Check if API key is provided
if (-not $ApiKey) {
    Write-Host "ERROR: Ghana NLP API key required!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please provide your API key:" -ForegroundColor Yellow
    Write-Host "  1. Set environment variable: `$env:GHANA_NLP_API_KEY = 'your_key'" -ForegroundColor Cyan
    Write-Host "  2. Or pass as parameter: .\setup-twi-greeting.ps1 -ApiKey 'your_key'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Get your API key from: https://translation.ghananlp.org/" -ForegroundColor Yellow
    exit 1
}

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found. Please install Python 3.7+" -ForegroundColor Red
    exit 1
}

# Check if ghana-nlp is installed
Write-Host "Checking ghana-nlp package..." -ForegroundColor Yellow
$packageCheck = python -c "import ghana_nlp" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ ghana-nlp not installed. Installing..." -ForegroundColor Yellow
    pip install ghana-nlp
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ Failed to install ghana-nlp" -ForegroundColor Red
        exit 1
    }
}
Write-Host "  ✓ ghana-nlp is installed" -ForegroundColor Green

# Generate Twi greeting
Write-Host ""
Write-Host "Generating Twi greeting audio..." -ForegroundColor Yellow
python generate_twi_greeting.py --api-key $ApiKey

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Failed to generate Twi greeting" -ForegroundColor Red
    exit 1
}

# Create FreeSWITCH sounds directory if it doesn't exist
Write-Host ""
Write-Host "Setting up FreeSWITCH sounds directory..." -ForegroundColor Yellow
if (-not (Test-Path $FreeSwitchSoundsPath)) {
    Write-Host "  Creating directory: $FreeSwitchSoundsPath" -ForegroundColor Cyan
    New-Item -ItemType Directory -Force -Path $FreeSwitchSoundsPath | Out-Null
}

# Copy audio file to FreeSWITCH
$sourceFile = "sounds\custom\twi_greeting.wav"
if (Test-Path $sourceFile) {
    Write-Host "  Copying audio file to FreeSWITCH..." -ForegroundColor Cyan
    Copy-Item -Path $sourceFile -Destination "$FreeSwitchSoundsPath\twi_greeting.wav" -Force
    Write-Host "  ✓ Audio file copied successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ Generated audio file not found: $sourceFile" -ForegroundColor Red
    exit 1
}

# Copy dialplan to FreeSWITCH
Write-Host ""
Write-Host "Updating FreeSWITCH dialplan..." -ForegroundColor Yellow
$dialplanSource = "conf\dialplan\default.xml"
$dialplanDest = "C:\Program Files\FreeSWITCH\conf\dialplan\default.xml"

if (Test-Path $dialplanSource) {
    Copy-Item -Path $dialplanSource -Destination $dialplanDest -Force
    Write-Host "  ✓ Dialplan updated" -ForegroundColor Green
} else {
    Write-Host "  ✗ Dialplan file not found: $dialplanSource" -ForegroundColor Red
    exit 1
}

# Reload FreeSWITCH
Write-Host ""
Write-Host "Reloading FreeSWITCH configuration..." -ForegroundColor Yellow
try {
    fs_cli -x "reloadxml" | Out-Null
    Write-Host "  ✓ FreeSWITCH configuration reloaded" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Could not reload FreeSWITCH automatically" -ForegroundColor Yellow
    Write-Host "  Please run manually: fs_cli -x 'reloadxml'" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Register your SIP client (MicroSIP/Linphone) with extension 1000" -ForegroundColor White
Write-Host "  2. Dial 1001 to test the Twi greeting" -ForegroundColor White
Write-Host "  3. You should hear the Twi greeting" -ForegroundColor White
Write-Host ""
