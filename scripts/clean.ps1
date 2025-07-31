$ErrorActionPreference = "SilentlyContinue"
Remove-Item .\logs\plan_cache.json -Force
Remove-Item .\logs\qa_run.json -Force
Remove-Item .\logs\report.md -Force
Write-Host "Cleaned logs & cache." -ForegroundColor Green
