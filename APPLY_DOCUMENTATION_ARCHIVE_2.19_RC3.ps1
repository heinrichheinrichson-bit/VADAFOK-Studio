$ErrorActionPreference = "Stop"
$ProjectRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)

$Mappings = @(
    [pscustomobject]@{ Source = "docs\BANNER_WORKFLOW_2.17_RC1_APPEND.md"; Destination = "docs\history\2.17\notes\BANNER_WORKFLOW_2.17_RC1_APPEND.md" }
    [pscustomobject]@{ Source = "docs\CLEANUP_ANALYZER_2.19_RC2.md"; Destination = "docs\history\2.19\notes\CLEANUP_ANALYZER_2.19_RC2.md" }
    [pscustomobject]@{ Source = "docs\CLEANUP_ANALYZER_2.19_RC2A.md"; Destination = "docs\history\2.19\notes\CLEANUP_ANALYZER_2.19_RC2A.md" }
    [pscustomobject]@{ Source = "docs\CLEANUP_ANALYZER_2.19_RC2B.md"; Destination = "docs\history\2.19\notes\CLEANUP_ANALYZER_2.19_RC2B.md" }
    [pscustomobject]@{ Source = "docs\CLEANUP_INVENTORY_2.19_RC1.md"; Destination = "docs\history\2.19\notes\CLEANUP_INVENTORY_2.19_RC1.md" }
    [pscustomobject]@{ Source = "docs\IDEAS_2.19_RC1_APPEND.md"; Destination = "docs\history\2.19\notes\IDEAS_2.19_RC1_APPEND.md" }
    [pscustomobject]@{ Source = "docs\OBS_ASSET_DISPLAY_IDEA_2.18_APPEND.md"; Destination = "docs\history\2.18\notes\OBS_ASSET_DISPLAY_IDEA_2.18_APPEND.md" }
    [pscustomobject]@{ Source = "docs\QUICK_CARDS_WORKFLOW_2.16.9_RC1.md"; Destination = "docs\history\2.16\notes\QUICK_CARDS_WORKFLOW_2.16.9_RC1.md" }
    [pscustomobject]@{ Source = "docs\RELEASE_CHECKLIST.md"; Destination = "docs\history\misc\release\RELEASE_CHECKLIST.md" }
    [pscustomobject]@{ Source = "docs\ROADMAP_2.19_RC1_APPEND.md"; Destination = "docs\history\2.19\notes\ROADMAP_2.19_RC1_APPEND.md" }
    [pscustomobject]@{ Source = "docs\STREAM_WORKFLOW_2.18_RC1.md"; Destination = "docs\history\2.18\notes\STREAM_WORKFLOW_2.18_RC1.md" }
    [pscustomobject]@{ Source = "docs\STREAM_WORKFLOW_2.18_RC1A.md"; Destination = "docs\history\2.18\notes\STREAM_WORKFLOW_2.18_RC1A.md" }
    [pscustomobject]@{ Source = "docs\STREAM_WORKFLOW_2.18_RC1B.md"; Destination = "docs\history\2.18\notes\STREAM_WORKFLOW_2.18_RC1B.md" }
    [pscustomobject]@{ Source = "docs\STREAM_WORKFLOW_2.18_RC1C.md"; Destination = "docs\history\2.18\notes\STREAM_WORKFLOW_2.18_RC1C.md" }
    [pscustomobject]@{ Source = "docs\STREAM_WORKFLOW_2.18_RC1D.md"; Destination = "docs\history\2.18\notes\STREAM_WORKFLOW_2.18_RC1D.md" }
    [pscustomobject]@{ Source = "docs\STREAM_WORKFLOW_2.18_RC1E.md"; Destination = "docs\history\2.18\notes\STREAM_WORKFLOW_2.18_RC1E.md" }
    [pscustomobject]@{ Source = "docs\VOICE_CONTROL_2.16.7_RC1_APPEND.md"; Destination = "docs\history\2.16\notes\VOICE_CONTROL_2.16.7_RC1_APPEND.md" }
    [pscustomobject]@{ Source = "docs\VOICE_QUICK_CARDS_2.16.8_RC1A.md"; Destination = "docs\history\2.16\notes\VOICE_QUICK_CARDS_2.16.8_RC1A.md" }
    [pscustomobject]@{ Source = "docs\VOICE_QUICK_CARDS_2.16.8_RC1B.md"; Destination = "docs\history\2.16\notes\VOICE_QUICK_CARDS_2.16.8_RC1B.md" }
    [pscustomobject]@{ Source = "docs\VOICE_QUICK_CARDS_2.16.8_RC1C.md"; Destination = "docs\history\2.16\notes\VOICE_QUICK_CARDS_2.16.8_RC1C.md" }
    [pscustomobject]@{ Source = "FINALIZE_RELEASE_2.16.6.bat"; Destination = "docs\history\2.16\release\FINALIZE_RELEASE_2.16.6.bat" }
    [pscustomobject]@{ Source = "INSTALLIEREN_UND_TESTEN_2.16.7_RC1.txt"; Destination = "docs\history\2.16\install\INSTALLIEREN_UND_TESTEN_2.16.7_RC1.txt" }
    [pscustomobject]@{ Source = "INSTALLIEREN_UND_TESTEN_2.16.8_RC1A.txt"; Destination = "docs\history\2.16\install\INSTALLIEREN_UND_TESTEN_2.16.8_RC1A.txt" }
    [pscustomobject]@{ Source = "INSTALLIEREN_UND_TESTEN_2.16.8_RC1B.txt"; Destination = "docs\history\2.16\install\INSTALLIEREN_UND_TESTEN_2.16.8_RC1B.txt" }
    [pscustomobject]@{ Source = "INSTALLIEREN_UND_TESTEN_2.16.8_RC1C.txt"; Destination = "docs\history\2.16\install\INSTALLIEREN_UND_TESTEN_2.16.8_RC1C.txt" }
    [pscustomobject]@{ Source = "INSTALLIEREN_UND_TESTEN_2.16.9_RC1.txt"; Destination = "docs\history\2.16\install\INSTALLIEREN_UND_TESTEN_2.16.9_RC1.txt" }
    [pscustomobject]@{ Source = "INSTALLIEREN_UND_TESTEN_2.17_RC1.txt"; Destination = "docs\history\2.17\install\INSTALLIEREN_UND_TESTEN_2.17_RC1.txt" }
    [pscustomobject]@{ Source = "INSTALLIEREN_UND_TESTEN_2.18_RC1.txt"; Destination = "docs\history\2.18\install\INSTALLIEREN_UND_TESTEN_2.18_RC1.txt" }
    [pscustomobject]@{ Source = "INSTALLIEREN_UND_TESTEN_2.18_RC1A.txt"; Destination = "docs\history\2.18\install\INSTALLIEREN_UND_TESTEN_2.18_RC1A.txt" }
    [pscustomobject]@{ Source = "INSTALLIEREN_UND_TESTEN_2.18_RC1B.txt"; Destination = "docs\history\2.18\install\INSTALLIEREN_UND_TESTEN_2.18_RC1B.txt" }
    [pscustomobject]@{ Source = "INSTALLIEREN_UND_TESTEN_2.18_RC1C.txt"; Destination = "docs\history\2.18\install\INSTALLIEREN_UND_TESTEN_2.18_RC1C.txt" }
    [pscustomobject]@{ Source = "INSTALLIEREN_UND_TESTEN_2.18_RC1D.txt"; Destination = "docs\history\2.18\install\INSTALLIEREN_UND_TESTEN_2.18_RC1D.txt" }
    [pscustomobject]@{ Source = "INSTALLIEREN_UND_TESTEN_2.18_RC1E.txt"; Destination = "docs\history\2.18\install\INSTALLIEREN_UND_TESTEN_2.18_RC1E.txt" }
    [pscustomobject]@{ Source = "INSTALLIEREN_UND_TESTEN_2.19_RC1.txt"; Destination = "docs\history\2.19\install\INSTALLIEREN_UND_TESTEN_2.19_RC1.txt" }
    [pscustomobject]@{ Source = "INSTALLIEREN_UND_TESTEN_2.19_RC2_ANALYZER.txt"; Destination = "docs\history\2.19\install\INSTALLIEREN_UND_TESTEN_2.19_RC2_ANALYZER.txt" }
    [pscustomobject]@{ Source = "INSTALLIEREN_UND_TESTEN_2.19_RC2A_ANALYZER_FIX.txt"; Destination = "docs\history\2.19\install\INSTALLIEREN_UND_TESTEN_2.19_RC2A_ANALYZER_FIX.txt" }
    [pscustomobject]@{ Source = "INSTALLIEREN_UND_TESTEN_2.19_RC2B_ANALYZER_PATH_FIX.txt"; Destination = "docs\history\2.19\install\INSTALLIEREN_UND_TESTEN_2.19_RC2B_ANALYZER_PATH_FIX.txt" }
    [pscustomobject]@{ Source = "RELEASE_2.16.6.md"; Destination = "docs\history\2.16\release\RELEASE_2.16.6.md" }
)

$LogDir = Join-Path $ProjectRoot "docs\history\_cleanup_logs"
$ManifestDir = Join-Path $ProjectRoot "docs\history\_cleanup_manifests"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
New-Item -ItemType Directory -Force -Path $ManifestDir | Out-Null

$LogPath = Join-Path $LogDir "2.19_RC3_documentation_archive.log"
$ManifestPath = Join-Path $ManifestDir "2.19_RC3_documentation_archive.json"

$Results = New-Object System.Collections.Generic.List[object]
$Moved = 0
$Skipped = 0
$Conflicts = 0

foreach ($Mapping in $Mappings) {
    $SourcePath = Join-Path $ProjectRoot $Mapping.Source
    $DestinationPath = Join-Path $ProjectRoot $Mapping.Destination

    if (-not (Test-Path -LiteralPath $SourcePath -PathType Leaf)) {
        $Results.Add([pscustomobject]@{
            Source = $Mapping.Source
            Destination = $Mapping.Destination
            Status = "SKIPPED_SOURCE_MISSING"
        })
        $Skipped++
        Write-Host "Skipped (missing): $($Mapping.Source)" -ForegroundColor DarkYellow
        continue
    }

    if (Test-Path -LiteralPath $DestinationPath -PathType Leaf) {
        $Results.Add([pscustomobject]@{
            Source = $Mapping.Source
            Destination = $Mapping.Destination
            Status = "CONFLICT_DESTINATION_EXISTS"
        })
        $Conflicts++
        Write-Host "Conflict (destination exists): $($Mapping.Destination)" -ForegroundColor Red
        continue
    }

    $DestinationDirectory = Split-Path -Parent $DestinationPath
    New-Item -ItemType Directory -Force -Path $DestinationDirectory | Out-Null
    Move-Item -LiteralPath $SourcePath -Destination $DestinationPath

    $Results.Add([pscustomobject]@{
        Source = $Mapping.Source
        Destination = $Mapping.Destination
        Status = "MOVED"
    })
    $Moved++
    Write-Host "Moved: $($Mapping.Source) -> $($Mapping.Destination)" -ForegroundColor Green
}

$Manifest = [pscustomobject]@{
    Version = "2.19 RC3"
    CreatedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    ProjectRoot = $ProjectRoot
    Moved = $Moved
    Skipped = $Skipped
    Conflicts = $Conflicts
    Results = $Results
}

$Manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8

$LogLines = @(
    "VADAFOK Studio 2.19 RC3 - Documentation Archive",
    "Created: $($Manifest.CreatedAt)",
    "Moved: $Moved",
    "Skipped: $Skipped",
    "Conflicts: $Conflicts",
    "",
    "No files were deleted.",
    ""
)
foreach ($Result in $Results) {
    $LogLines += "$($Result.Status): $($Result.Source) -> $($Result.Destination)"
}
[System.IO.File]::WriteAllLines($LogPath, $LogLines, (New-Object System.Text.UTF8Encoding($false)))

Write-Host ""
Write-Host "Documentation archive complete." -ForegroundColor Green
Write-Host "Moved: $Moved"
Write-Host "Skipped: $Skipped"
Write-Host "Conflicts: $Conflicts"
Write-Host "No files were deleted." -ForegroundColor Green
Write-Host ""
Write-Host "Manifest: $ManifestPath"
Write-Host "Log:      $LogPath"

if ($Conflicts -gt 0) {
    Write-Host ""
    Write-Host "Archive completed with conflicts. Do not commit until reviewed." -ForegroundColor Red
    exit 2
}
