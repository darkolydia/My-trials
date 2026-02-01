# Watch live_log.txt. Dial 1002, speak - your transcribed question appears here.
# Run: .\watch-live-log.ps1

$liveLog = "C:\Users\User\Desktop\Recordings\live_log.txt"
$liveLogDir = "C:\Users\User\Desktop\Recordings"
if (-not (Test-Path $liveLogDir)) { New-Item -Path $liveLogDir -ItemType Directory -Force | Out-Null }
if (-not (Test-Path $liveLog)) { New-Item -Path $liveLog -ItemType File -Force | Out-Null }

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host "=========================================="
Write-Host "  Live log watcher: $liveLog"
Write-Host "  Dial 1002, speak your question."
Write-Host "  Ctrl+C to stop."
Write-Host "=========================================="
Write-Host ""

$lastCount = 0
$tick = 0
while ($true) {
    $lines = @(Get-Content $liveLog -ErrorAction SilentlyContinue)
    $n = $lines.Count
    if ($n -gt $lastCount) {
        for ($i = $lastCount; $i -lt $n; $i++) {
            Write-Host $lines[$i]
        }
        $lastCount = $n
    }
    $tick++
    if ($n -eq 0 -and ($tick -eq 1 -or ($tick % 10 -eq 0))) {
        Write-Host "[waiting for calls...]"
    }
    Start-Sleep -Seconds 1
}
