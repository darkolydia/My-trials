# Quick Start Script for English Voice Assistant
# This script helps you get started quickly

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "English Voice Assistant - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found! Please install Python 3.7+" -ForegroundColor Red
    exit 1
}

# Check if we're in the right directory
$currentDir = Get-Location
if (-not (Test-Path "voice_assistant.py")) {
    Write-Host "✗ voice_assistant.py not found!" -ForegroundColor Red
    Write-Host "Please run this script from the english_voice_assistant folder" -ForegroundColor Yellow
    exit 1
}

# Check dependencies
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$depsInstalled = $true
try {
    python -c "import ghana_nlp" 2>$null
    if ($LASTEXITCODE -ne 0) { $depsInstalled = $false }
} catch {
    $depsInstalled = $false
}

if (-not $depsInstalled) {
    Write-Host "✗ Dependencies not installed" -ForegroundColor Red
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✓ Dependencies already installed" -ForegroundColor Green
}

# Check .env file
Write-Host ""
Write-Host "Checking API key configuration..." -ForegroundColor Yellow
$envFile = ".env"
$parentEnvFile = "..\.env"

if (Test-Path $envFile) {
    Write-Host "✓ Found .env file in current directory" -ForegroundColor Green
} elseif (Test-Path $parentEnvFile) {
    Write-Host "✓ Found .env file in parent directory" -ForegroundColor Green
} else {
    Write-Host "✗ No .env file found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    $apiKey = Read-Host "Enter your Ghana NLP API key"
    if ($apiKey) {
        "GHANANLP_API_KEY=$apiKey" | Out-File -FilePath $envFile -Encoding utf8
        Write-Host "✓ Created .env file" -ForegroundColor Green
    } else {
        Write-Host "✗ No API key provided. Please create .env file manually." -ForegroundColor Red
        Write-Host "   Add: GHANANLP_API_KEY=your_api_key_here" -ForegroundColor Yellow
    }
}

# Test the system
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing the system..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Running test: python voice_assistant.py --text 'hello'" -ForegroundColor Yellow
python voice_assistant.py --text "hello"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ Setup Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. View Q&A pairs: python manage_qa.py --list" -ForegroundColor White
    Write-Host "2. Test questions: python test_qa.py" -ForegroundColor White
    Write-Host "3. Add your Q&A pairs: Edit voice_assistant.py" -ForegroundColor White
    Write-Host ""
    Write-Host "See GETTING_STARTED.md for more details" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "✗ Test failed. Please check the error messages above." -ForegroundColor Red
    Write-Host "See GETTING_STARTED.md for troubleshooting" -ForegroundColor Yellow
}
