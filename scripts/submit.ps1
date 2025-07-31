param(
  [string]$Goal = "Toggle WiFi off then back on"
)

$ErrorActionPreference = "Stop"

.\scripts\clean.ps1

$useLLM = [bool]$env:OPENAI_API_KEY
if ($useLLM) {
  .\scripts\run-demo.ps1 -UseLLM -Goal $Goal
} else {
  .\scripts\run-demo.ps1 -Goal $Goal
}

.\scripts\package.ps1
