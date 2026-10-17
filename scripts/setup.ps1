<#
.SYNOPSIS
    Set up the shared workshop on Windows with existing Python, Node and FFmpeg.
.EXAMPLE
    .\scripts\setup.ps1 -Agent both -Audio
#>
[CmdletBinding()]
param(
    [ValidateSet('claude', 'codex', 'both')][string]$Agent = 'claude',
    [switch]$Audio,
    [switch]$Transcription,
    [switch]$SkillsOnly
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$env:PYTHONUTF8 = '1'

function Invoke-Checked {
    param([string]$Program, [string[]]$Arguments)
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Program failed (exit $LASTEXITCODE)." }
}

Push-Location $projectRoot
try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Install Git and reopen PowerShell.' }
    $venvPython = Join-Path $projectRoot '.venv/Scripts/python.exe'
    if ($SkillsOnly) {
        $bootstrapPython = if (Test-Path -LiteralPath $venvPython) { $venvPython } else { 'python' }
        Invoke-Checked $bootstrapPython @('scripts/skills.py', 'install', '--target', $Agent)
        return
    }
    foreach ($tool in @('node', 'npm.cmd', 'ffmpeg', 'ffprobe')) {
        if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "Install $tool and reopen PowerShell. See README.md." }
    }
    if ([int]((& node --version).TrimStart('v').Split('.')[0]) -lt 22) { throw 'Node.js 22 or newer is required.' }
    if (-not (Test-Path -LiteralPath $venvPython)) {
        if (Get-Command py -ErrorAction SilentlyContinue) {
            Invoke-Checked 'py' @('-3.12', '-m', 'venv', '.venv')
        } else {
            Invoke-Checked 'python' @('-c', 'import sys; assert sys.version_info[:2] == (3, 12), "Install Python 3.12"')
            Invoke-Checked 'python' @('-m', 'venv', '.venv')
        }
    }
    Invoke-Checked $venvPython @('-m', 'pip', 'install', '-r', 'requirements.txt')
    if ($Audio) { Invoke-Checked $venvPython @('-m', 'pip', 'install', '-r', 'requirements-audio.txt') }
    if ($Transcription) { Invoke-Checked $venvPython @('-m', 'pip', 'install', '-r', 'requirements-transcription.txt') }
    Invoke-Checked 'npm.cmd' @('ci')
    Invoke-Checked $venvPython @('scripts/skills.py', 'install', '--target', $Agent)
    Invoke-Checked $venvPython @('scripts/doctor.py', '--target', $Agent)
    Write-Output 'Workshop ready. Activate .venv/Scripts/Activate.ps1 before working.'
} finally {
    Pop-Location
}
