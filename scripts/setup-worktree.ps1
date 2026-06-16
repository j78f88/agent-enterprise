# Bootstrap a fresh git worktree so it can build (Windows).
#
# A linked worktree starts with no resolved/ tree and no installed deps.
# Run this once after `git worktree add` (e.g. when an agent gets its own
# worktree) to install runtime deps and produce a working resolved/ tree.
#
# Worktree-safe: resolves the repo root via `git rev-parse --show-toplevel`
# rather than assuming an absolute path, so it behaves correctly from any
# linked worktree.
#
# Usage:
#   .\scripts\setup-worktree.ps1 [-Config <path>]

[CmdletBinding()]
param(
    [string]$Config = "config/project.config.example.yml"
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"

$root = (git rev-parse --show-toplevel)
if ($LASTEXITCODE -ne 0) { throw "not inside a git worktree" }
Set-Location $root

Write-Host "=== agent-enterprise worktree setup ==="
Write-Host "Worktree: $root"
Write-Host "Python:   $(python --version)"
Write-Host "Config:   $Config"
Write-Host ""

Write-Host "--- 1/2 install runtime deps ---"
python -m pip install --quiet -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "pip install runtime failed" }

Write-Host "--- 2/2 build resolved/ artifacts ---"
python init.py --config $Config
if ($LASTEXITCODE -ne 0) { throw "init.py failed" }

Write-Host ""
Write-Host "=== worktree ready ==="
