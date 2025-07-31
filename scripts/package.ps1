$ErrorActionPreference = "Stop"
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$zip = ".\artifact-$stamp.zip"

# Confirm outputs exist (warn if not)
if (-not (Test-Path ".\logs\qa_run.json") -or -not (Test-Path ".\logs\report.md")) {
  Write-Warning "Run the demo first so qa_run.json and report.md exist."
}

# What to include
$items = @(
  "README.md",
  "requirements.txt",
  "Dockerfile",
  "scripts",
  "src",
  "tests",
  "logs\qa_run.json",
  "logs\report.md"
)

if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path $items -DestinationPath $zip -Force
Write-Host "Created package: $zip" -ForegroundColor Green
