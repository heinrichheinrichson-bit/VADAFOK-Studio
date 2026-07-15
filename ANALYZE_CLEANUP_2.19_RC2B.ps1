param(
    [string]$ProjectRoot = ""
)

$ErrorActionPreference = "Stop"

# The batch launcher intentionally passes no path. This avoids malformed
# arguments when the project directory contains spaces and ends in "\".
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = $PSScriptRoot
}

# Defensive cleanup in case the script is started manually with a quoted path.
$ProjectRoot = $ProjectRoot.Trim().Trim('"')
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)

if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) {
    throw "Projektordner wurde nicht gefunden: $ProjectRoot"
}

$ReportDir = Join-Path $ProjectRoot "docs\cleanup_reports\2.19_RC2B"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$ExcludedDirectories = @(
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "env",
    "node_modules"
)

function Get-RelativePath {
    param([string]$FullPath)

    $rootWithSeparator = $ProjectRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    $rootUri = [System.Uri]::new($rootWithSeparator)
    $fileUri = [System.Uri]::new($FullPath)
    $relative = $rootUri.MakeRelativeUri($fileUri).ToString()
    return [System.Uri]::UnescapeDataString($relative).Replace('/', '\')
}

function Escape-Markdown {
    param([string]$Value)

    if ($null -eq $Value) { return "" }
    return $Value.Replace('|', '\|').Replace("`r", " ").Replace("`n", " ")
}

function Get-Classification {
    param(
        [string]$RelativePath,
        [string]$Extension,
        [string]$FileName
    )

    $pathLower = $RelativePath.ToLowerInvariant()
    $nameLower = $FileName.ToLowerInvariant()
    $extLower = $Extension.ToLowerInvariant()

    $activeExact = @(
        "readme.md",
        "project_rules.md",
        "roadmap.md",
        "requirements.txt",
        "requirements_voice.txt",
        "run.py",
        "start vadafok studio.bat",
        ".gitignore"
    )

    if ($activeExact -contains $pathLower) {
        return [pscustomobject]@{
            Status = "ACTIVE"
            Confidence = "HIGH"
            Reason = "Aktive Projekt-, Start-, Abhängigkeits- oder Kerndatei."
            Suggestion = "Behalten"
        }
    }

    if ($pathLower -match '^docs\\(ideas|master_roadmap|roadmap|architecture|changelog|voice_control|project_structure)\.md$') {
        return [pscustomobject]@{
            Status = "ACTIVE"
            Confidence = "HIGH"
            Reason = "Aktive Kerndokumentation."
            Suggestion = "Behalten und weiter ergänzen"
        }
    }

    if ($pathLower -match '^(vadafok_studio|tools|styles|assets|library|batch_projects)\\') {
        return [pscustomobject]@{
            Status = "ACTIVE"
            Confidence = "HIGH"
            Reason = "Quellcode, Werkzeuge, Styles oder Laufzeit-Assets."
            Suggestion = "Behalten"
        }
    }

    if ($nameLower -match '^installieren_und_testen_.*\.(txt|md)$') {
        $versionBucket = "misc"
        if ($nameLower -match '(2\.\d+)') { $versionBucket = $Matches[1] }
        return [pscustomobject]@{
            Status = "ARCHIVE_CANDIDATE"
            Confidence = "HIGH"
            Reason = "Versionsgebundene Installations- oder RC/Test-Anleitung."
            Suggestion = "docs\history\$versionBucket\install\"
        }
    }

    if ($nameLower -match '(^|_)(rc\d*[a-z]?|test\d+|append)(_|\.|$)' -and $extLower -in @(".md", ".txt")) {
        $versionBucket = "misc"
        if ($nameLower -match '(2\.\d+)') { $versionBucket = $Matches[1] }
        return [pscustomobject]@{
            Status = "ARCHIVE_CANDIDATE"
            Confidence = "HIGH"
            Reason = "Historische RC-, Test- oder Ergänzungsnotiz."
            Suggestion = "docs\history\$versionBucket\notes\"
        }
    }

    if ($nameLower -match '^finalize_release_.*\.(bat|ps1)$' -or $nameLower -match '^release_.*\.md$') {
        $versionBucket = "misc"
        if ($nameLower -match '(2\.\d+)') { $versionBucket = $Matches[1] }
        return [pscustomobject]@{
            Status = "ARCHIVE_CANDIDATE"
            Confidence = "HIGH"
            Reason = "Historisches Release-Werkzeug oder Release-Dokument."
            Suggestion = "docs\history\$versionBucket\release\"
        }
    }

    if ($pathLower -match '^exports\\') {
        if ($nameLower -match '_preview\.(png|jpg|jpeg|webp)$') {
            return [pscustomobject]@{
                Status = "REVIEW"
                Confidence = "HIGH"
                Reason = "Erzeugte Export-Vorschau; möglicherweise nicht zur Versionierung bestimmt."
                Suggestion = "Prüfen; eventuell .gitignore ergänzen"
            }
        }

        return [pscustomobject]@{
            Status = "REVIEW"
            Confidence = "MEDIUM"
            Reason = "Exportdatei: absichtlich versioniert oder generiert?"
            Suggestion = "Manuell entscheiden"
        }
    }

    if ($pathLower -match '^(data|exports)\\') {
        return [pscustomobject]@{
            Status = "REVIEW"
            Confidence = "MEDIUM"
            Reason = "Laufzeit- oder Benutzerdaten; nicht automatisch archivieren."
            Suggestion = "Behalten, bis Nutzung geklärt ist"
        }
    }

    if ($extLower -in @(".py", ".ps1", ".bat", ".json", ".yaml", ".yml", ".toml", ".ini", ".png", ".jpg", ".jpeg", ".webp", ".ico", ".svg", ".ttf", ".otf")) {
        return [pscustomobject]@{
            Status = "ACTIVE"
            Confidence = "HIGH"
            Reason = "Quellcode, Konfiguration oder Laufzeit-Asset."
            Suggestion = "Behalten"
        }
    }

    if ($extLower -in @(".md", ".txt")) {
        return [pscustomobject]@{
            Status = "REVIEW"
            Confidence = "MEDIUM"
            Reason = "Dokumentation ohne eindeutiges Aktiv-/Archiv-Signal."
            Suggestion = "Inhalt prüfen"
        }
    }

    if ($extLower -eq ".zip") {
        return [pscustomobject]@{
            Status = "REVIEW"
            Confidence = "HIGH"
            Reason = "Eingechecktes Archiv; Nutzen und Aktualität prüfen."
            Suggestion = "Manuell entscheiden"
        }
    }

    return [pscustomobject]@{
        Status = "REVIEW"
        Confidence = "LOW"
        Reason = "Keine sichere automatische Klassifikation."
        Suggestion = "Manuell prüfen"
    }
}

$files = Get-ChildItem -LiteralPath $ProjectRoot -File -Recurse -Force | Where-Object {
    $relative = Get-RelativePath -FullPath $_.FullName
    $parts = $relative -split '\\'
    $excluded = $false

    foreach ($part in $parts) {
        if ($ExcludedDirectories -contains $part) {
            $excluded = $true
            break
        }
    }

    if ($relative -like "docs\cleanup_reports\2.19_RC2B\*") {
        $excluded = $true
    }

    -not $excluded
}

$inventory = foreach ($file in $files) {
    $relativePath = Get-RelativePath -FullPath $file.FullName
    $classification = Get-Classification `
        -RelativePath $relativePath `
        -Extension $file.Extension `
        -FileName $file.Name

    [pscustomobject]@{
        Path = $relativePath
        Status = $classification.Status
        Confidence = $classification.Confidence
        Reason = $classification.Reason
        Suggestion = $classification.Suggestion
        SizeBytes = $file.Length
        Modified = $file.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
    }
}

$inventory = @($inventory | Sort-Object Status, Path)

$csvPath = Join-Path $ReportDir "cleanup_inventory.csv"
$jsonPath = Join-Path $ReportDir "cleanup_inventory.json"
$mdPath = Join-Path $ReportDir "cleanup_report.md"

$inventory | Export-Csv -LiteralPath $csvPath -NoTypeInformation -Encoding UTF8
$inventory | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

$statusOrder = @("ACTIVE", "ARCHIVE_CANDIDATE", "REMOVE_CANDIDATE", "REVIEW")
$counts = @{}
foreach ($status in $statusOrder) {
    $counts[$status] = @($inventory | Where-Object Status -eq $status).Count
}

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# VADAFOK Studio – Cleanup Analyzer 2.19 RC2B")
$lines.Add("")
$lines.Add("> Diese Analyse hat keine Projektdateien verschoben, umbenannt oder gelöscht.")
$lines.Add("")
$lines.Add("## Zusammenfassung")
$lines.Add("")
$lines.Add("| Status | Anzahl |")
$lines.Add("|---|---:|")
foreach ($status in $statusOrder) {
    $lines.Add("| $status | $($counts[$status]) |")
}
$lines.Add("")
$lines.Add("## Bedeutung")
$lines.Add("")
$lines.Add("- **ACTIVE:** mit hoher Sicherheit aktiv; nicht archivieren.")
$lines.Add("- **ARCHIVE_CANDIDATE:** wahrscheinlich historische Test-/Release-Dokumentation; Inhalt bleibt zu erhalten.")
$lines.Add("- **REMOVE_CANDIDATE:** wahrscheinlich generiert oder entbehrlich; vor Entfernen bestätigen.")
$lines.Add("- **REVIEW:** nicht automatisch entscheiden; gezielt prüfen.")
$lines.Add("")

foreach ($status in $statusOrder) {
    $items = @($inventory | Where-Object Status -eq $status)
    $lines.Add("## $status ($($items.Count))")
    $lines.Add("")
    $lines.Add("| Datei | Sicherheit | Begründung | Vorschlag |")
    $lines.Add("|---|---|---|---|")

    foreach ($item in $items) {
        $safePath = Escape-Markdown -Value $item.Path
        $safeConfidence = Escape-Markdown -Value $item.Confidence
        $safeReason = Escape-Markdown -Value $item.Reason
        $safeSuggestion = Escape-Markdown -Value $item.Suggestion
        $lines.Add("| $safePath | $safeConfidence | $safeReason | $safeSuggestion |")
    }

    $lines.Add("")
}

$lines.Add("## Nächster Schritt")
$lines.Add("")
$lines.Add("Sende vorzugsweise nur `cleanup_report.md`. Daraus kann ein kontrolliertes Archivpaket erstellt werden. Einzel-Screenshots sind nicht nötig.")

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllLines($mdPath, $lines, $utf8NoBom)

Write-Host ""
Write-Host "Cleanup analysis complete." -ForegroundColor Green
Write-Host "No project files were moved or deleted." -ForegroundColor Green
Write-Host ""
Write-Host "Project root:" -ForegroundColor Cyan
Write-Host "  $ProjectRoot"
Write-Host ""
Write-Host "Report:" -ForegroundColor Cyan
Write-Host "  $mdPath"
Write-Host ""
Write-Host "Inventory:"
Write-Host "  $csvPath"
Write-Host "  $jsonPath"
Write-Host ""
Write-Host "Files analyzed: $($inventory.Count)"
foreach ($status in $statusOrder) {
    Write-Host "$status`: $($counts[$status])"
}
