# Test script for voice assistant
Write-Host "Testing Voice Assistant..." -ForegroundColor Green

# Check if recording exists
$recordingPath = "C:\Program Files\FreeSWITCH\recordings\user_question.wav"
if (Test-Path $recordingPath) {
    Write-Host "✓ Recording file exists: $recordingPath" -ForegroundColor Green
    $file = Get-Item $recordingPath
    Write-Host "  Size: $($file.Length) bytes" -ForegroundColor Cyan
    Write-Host "  Modified: $($file.LastWriteTime)" -ForegroundColor Cyan
} else {
    Write-Host "✗ Recording file NOT found: $recordingPath" -ForegroundColor Red
    Write-Host "  This means the recording didn't work." -ForegroundColor Yellow
}

# Test Python script
Write-Host "`nTesting Python script..." -ForegroundColor Green
$testAudio = "C:\Program Files\FreeSWITCH\recordings\user_question.wav"
$outputAudio = "C:\Program Files\FreeSWITCH\sounds\custom\response.wav"

if (Test-Path $testAudio) {
    Write-Host "Running voice_assistant.py..." -ForegroundColor Yellow
    python "C:\Users\User\Desktop\FreeSWITCH-to-linphone\voice_assistant.py" $testAudio -o $outputAudio
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Script executed successfully" -ForegroundColor Green
        if (Test-Path $outputAudio) {
            Write-Host "✓ Response file created: $outputAudio" -ForegroundColor Green
        } else {
            Write-Host "✗ Response file NOT created" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ Script failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    }
} else {
    Write-Host "Cannot test - recording file does not exist" -ForegroundColor Yellow
    Write-Host "Make a call to 1002 first to create the recording" -ForegroundColor Yellow
}
