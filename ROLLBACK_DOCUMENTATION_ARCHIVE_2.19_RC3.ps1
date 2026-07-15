$ErrorActionPreference = "Stop"
$ProjectRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
$ManifestPath = Join-Path $ProjectRoot "docs\history\_cleanup_manifests\2.19_RC3_documentation_archive.json"

if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
    throw "Rollback-Manifest nicht gefunden: $ManifestPath"
}

$Manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$MovedEntries = @($Manifest.Results | Where-Object Status -eq "MOVED")

$Restored = 0
$Skipped = 0
$Conflicts = 0

foreach ($Entry in ($MovedEntries | Sort-Object Destination -Descending)) {
    $ArchivedPath = Join-Path $ProjectRoot $Entry.Destination
    $OriginalPath = Join-Path $ProjectRoot $Entry.Source

    if (-not (Test-Path -LiteralPath $ArchivedPath -PathType Leaf)) {
        Write-Host "Skipped (archive missing): $($Entry.Destination)" -ForegroundColor DarkYellow
        $Skipped++
        continue
    }

    if (Test-Path -LiteralPath $OriginalPath -PathType Leaf) {
        Write-Host "Conflict (original exists): $($Entry.Source)" -ForegroundColor Red
        $Conflicts++
        continue
    }

    $OriginalDirectory = Split-Path -Parent $OriginalPath
    if (-not [string]::IsNullOrWhiteSpace($OriginalDirectory)) {
        New-Item -ItemType Directory -Force -Path $OriginalDirectory | Out-Null
    }

    Move-Item -LiteralPath $ArchivedPath -Destination $OriginalPath
    Write-Host "Restored: $($Entry.Destination) -> $($Entry.Source)" -ForegroundColor Green
    $Restored++
}

Write-Host ""
Write-Host "Documentation archive rollback complete." -ForegroundColor Green
Write-Host "Restored: $Restored"
Write-Host "Skipped: $Skipped"
Write-Host "Conflicts: $Conflicts"
Write-Host "No files were deleted." -ForegroundColor Green

if ($Conflicts -gt 0) {
    exit 2
}
