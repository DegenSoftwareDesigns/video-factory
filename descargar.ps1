<#
.SYNOPSIS
    Download a video with yt-dlp into downloads/<Categoria>.

.EXAMPLE
    .\descargar.ps1 "https://youtu.be/xxxx" references
    .\descargar.ps1 "https://youtu.be/xxxx" music -Audio
    .\descargar.ps1 "https://youtu.be/xxxx" b-roll/nature --download-sections "*1:00-2:30"
#>
param(
    [Parameter(Mandatory, Position = 0)][string]$Url,
    [Parameter(Mandatory, Position = 1)][string]$Categoria,
    # Extract audio only (m4a)
    [switch]$Audio,
    # Any extra yt-dlp arguments are passed through as-is
    [Parameter(ValueFromRemainingArguments)][string[]]$Extra
)

$ErrorActionPreference = 'Stop'

# Letters, digits, spaces, '-' and '_'; '/' allowed for subfolders; no '..'
if ($Categoria -notmatch '^[\w\- ]+(/[\w\- ]+)*$') {
    throw "Categoria no valida: '$Categoria'. Usa letras, numeros, espacios, '-', '_' y '/' para subcarpetas."
}

$root = $PSScriptRoot
$ytdlp = Join-Path $root '.venv\Scripts\yt-dlp.exe'
$config = Join-Path $root 'yt-dlp.conf'
$dest = Join-Path $root (Join-Path 'downloads' $Categoria)

$ytArgs = @('--config-location', $config, '-P', $dest)
if ($Audio) {
    $ytArgs += @('-f', 'ba/b', '-x', '--audio-format', 'm4a')
}
if ($Extra) { $ytArgs += $Extra }
$ytArgs += $Url

& $ytdlp @ytArgs
exit $LASTEXITCODE
