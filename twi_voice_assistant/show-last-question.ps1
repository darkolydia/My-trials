# Open last_question.txt in Notepad. Run this after each 1002 call to see
# what the system heard and answered. No watcher needed.
# Run: .\show-last-question.ps1

$f = "C:\Users\User\Desktop\Recordings\last_question.txt"
$d = "C:\Users\User\Desktop\Recordings"
if (-not (Test-Path $d)) { New-Item -Path $d -ItemType Directory -Force | Out-Null }
if (-not (Test-Path $f)) {
    Set-Content -Path $f -Value "transcript_twi: (no call yet)`nquestion_en: (no call yet)`nanswer_en: (no call yet)" -Encoding UTF8
}
Notepad $f
