# Canonical install + verification path for agent-enterprise (Windows).
# Runs from a clean checkout. Exits non-zero on any failure.
#
# Usage:
#   .\scripts\smoke-test.ps1 [-Config <path>]

[CmdletBinding()]
param(
    [string]$Config = "profiles/python-api.config.yml"
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"

function Get-ResolvedHash {
    $files = Get-ChildItem resolved -Recurse -File | Sort-Object FullName
    $hashes = $files | ForEach-Object { (Get-FileHash $_.FullName -Algorithm SHA256).Hash }
    $combined = ($hashes -join "")
    $stream = [IO.MemoryStream]::new([Text.Encoding]::ASCII.GetBytes($combined))
    return (Get-FileHash -InputStream $stream -Algorithm SHA256).Hash
}

Write-Host "=== agent-enterprise smoke test ==="
Write-Host "Python:  $(python --version)"
Write-Host "Config:  $Config"
Write-Host ""

Write-Host "--- 1/4 install runtime deps ---"
python -m pip install --quiet -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "pip install runtime failed" }

Write-Host "--- 2/4 install dev deps ---"
python -m pip install --quiet -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw "pip install dev failed" }

Write-Host "--- 3/4 build (twice, determinism check) ---"
if (Test-Path resolved) { Remove-Item resolved -Recurse -Force }
python init.py --config $Config | Out-Null
if ($LASTEXITCODE -ne 0) { throw "init.py run 1 failed" }
$h1 = Get-ResolvedHash
if (Test-Path resolved) { Remove-Item resolved -Recurse -Force }
python init.py --config $Config | Out-Null
if ($LASTEXITCODE -ne 0) { throw "init.py run 2 failed" }
$h2 = Get-ResolvedHash
if ($h1 -ne $h2) {
    Write-Host "FAIL: resolved/ output differs across two builds"
    Write-Host "  run 1: $h1"
    Write-Host "  run 2: $h2"
    # Show which files differ for diagnostics
    Write-Host "  file count run1 vs run2 may differ or content changed"
    exit 1
}
Write-Host "OK: byte-identical resolved/ ($h1)"

Write-Host "--- 4/4 pytest ---"
python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "pytest failed" }

Write-Host ""
Write-Host "=== smoke test PASS ==="
