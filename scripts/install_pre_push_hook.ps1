Param()

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$hookDir = Join-Path $repoRoot ".git\hooks"
$hookPath = Join-Path $hookDir "pre-push"

if (-not (Test-Path $hookDir)) {
    New-Item -ItemType Directory -Path $hookDir -Force | Out-Null
}

$hookBody = @"
#!/bin/sh
python scripts/secret_scan.py
"@

Set-Content -Path $hookPath -Value $hookBody -NoNewline

Write-Host "Installed pre-push hook at $hookPath"
