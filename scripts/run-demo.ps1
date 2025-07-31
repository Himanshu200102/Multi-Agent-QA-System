param(
  [string]$Goal = "Toggle WiFi off then back on",
  [switch]$UseLLM
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "=== Run Demo (LLM optional) ===" -ForegroundColor Cyan
Write-Host "CWD: $(Get-Location)"

# 1) Activate venv
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
  throw "Virtual env not found: .\.venv\Scripts\Activate.ps1"
}
. .\.venv\Scripts\Activate.ps1
Write-Host "Venv activated: $($env:VIRTUAL_ENV)" -ForegroundColor DarkCyan

# 2) Ensure Python can import from src/
$env:PYTHONPATH = (Resolve-Path .\src).Path
Write-Host "PYTHONPATH=$($env:PYTHONPATH)"

# 3) Ensure logs dir
$logs = ".\logs"
if (-not (Test-Path $logs)) { New-Item -ItemType Directory $logs | Out-Null }
Write-Host "Logs dir: $logs"

# 4) Echo params
Write-Host "Goal: $Goal"

# 5) Decide LLM usage
$useLLM = $UseLLM.IsPresent -or [bool]$env:OPENAI_API_KEY
$model = if ($env:OPENAI_MODEL) { $env:OPENAI_MODEL } else { "gpt-4o-mini" }
Write-Host "Use LLM: $useLLM  (OPENAI_API_KEY present: $([bool]$env:OPENAI_API_KEY))"
Write-Host "Model: $model"

# 6) Show Python being used
$py = (Get-Command python).Path
Write-Host "Python: $py"

# 7) Build and run command (separate exe + args)
$exe  = (Get-Command python).Source
$args = @("-m","qa_agents.run_test","--goal",$Goal,"--env","mock","--logs_dir",$logs)
if ($useLLM) { $args += @("--llm_planner","--model",$model) }

Write-Host "Running: $exe $($args -join ' ')" -ForegroundColor Cyan
& $exe @args

Write-Host "=== Done ===" -ForegroundColor Green
