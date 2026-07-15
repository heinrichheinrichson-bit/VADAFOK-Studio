[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ReportDir = Join-Path $Root 'docs\cleanup_reports\2.19_RC2'
New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null

$skipDirs = @('.git', '__pycache__', '.venv', 'venv', 'node_modules', 'docs\cleanup_reports')
$activeExact = @(
  'README.md','PROJECT_RULES.md','ROADMAP.md','requirements.txt','requirements_voice.txt',
  'run.py','Start VADAFOK Studio.bat','.gitignore','text_library.json','caption_library.json',
  'scene_favorites.json','silent_director_presets.json'
)
$activeDocNames = @('IDEAS.md','MASTER_ROADMAP.md','ROADMAP.md','ARCHITECTURE.md','CHANGELOG.md','VOICE_CONTROL.md','PROJECT_STRUCTURE.md')

function Get-RelativePath([string]$FullName) {
  return $FullName.Substring($Root.Length).TrimStart('\','/').Replace('\','/')
}

function Test-Skipped([string]$Relative) {
  foreach ($dir in $skipDirs) {
    $normalized = $dir.Replace('\','/').TrimEnd('/')
    if ($Relative -eq $normalized -or $Relative.StartsWith($normalized + '/')) { return $true }
  }
  return $false
}

function Classify-File([string]$Relative, [System.IO.FileInfo]$File) {
  $name = $File.Name
  $upper = $name.ToUpperInvariant()
  $ext = $File.Extension.ToLowerInvariant()
  $dir = (Split-Path $Relative -Parent).Replace('\','/')

  if ($activeExact -contains $Relative -or ($dir -eq 'docs' -and $activeDocNames -contains $name)) {
    return @{ Status='ACTIVE'; Confidence='HIGH'; Reason='Aktive Projekt-, Start-, Abhängigkeits- oder Kerndokumentation.' }
  }
  if ($Relative.StartsWith('vadafok_studio/') -or $Relative.StartsWith('tools/') -or $Relative.StartsWith('styles/') -or $Relative.StartsWith('assets/') -or $Relative.StartsWith('library/') -or $Relative.StartsWith('batch_projects/')) {
    return @{ Status='ACTIVE'; Confidence='HIGH'; Reason='Quellcode, Werkzeuge, Styles oder Laufzeit-Assets.' }
  }
  if ($Relative.StartsWith('data/')) {
    return @{ Status='REVIEW'; Confidence='MEDIUM'; Reason='Laufzeitdaten: vor Archivierung prüfen, ob benutzerspezifisch oder generiert.' }
  }
  if ($upper -match '^INSTALLIEREN_UND_TESTEN_' -or $upper -match '(^|_)RC[0-9A-Z]*([._-]|$)' -or $upper -match 'TEST[0-9]+') {
    return @{ Status='ARCHIVE_CANDIDATE'; Confidence='HIGH'; Reason='Versionsgebundene Installations- oder RC/Test-Anleitung.' }
  }
  if ($upper -match '^FINALIZE_RELEASE_' -or $upper -match '^RELEASE_[0-9]') {
    return @{ Status='ARCHIVE_CANDIDATE'; Confidence='HIGH'; Reason='Historisches Release-Werkzeug oder Release-Notiz.' }
  }
  if ($Relative.StartsWith('docs/') -and ($upper -match '_APPEND' -or $upper -match 'RC[0-9A-Z]*' -or $upper -match 'TEST[0-9]+')) {
    return @{ Status='ARCHIVE_CANDIDATE'; Confidence='HIGH'; Reason='Historische Dokument-Ergänzung oder Testnotiz.' }
  }
  if ($Relative.StartsWith('exports/')) {
    if ($upper -match '_PREVIEW\.(PNG|JPG|JPEG)$') {
      return @{ Status='REVIEW'; Confidence='HIGH'; Reason='Erzeugte Export-Vorschau; prüfen, ob sie versioniert werden soll.' }
    }
    return @{ Status='REVIEW'; Confidence='MEDIUM'; Reason='Exportdatei: absichtlich versioniert oder generiert?' }
  }
  if ($ext -in @('.pyc','.pyo','.tmp','.log')) {
    return @{ Status='REMOVE_CANDIDATE'; Confidence='HIGH'; Reason='Generierte Cache-, temporäre oder Logdatei.' }
  }
  if ($name -eq 'VADAFOK_CODE_ONLY.zip') {
    return @{ Status='REVIEW'; Confidence='HIGH'; Reason='Eingechecktes Archiv; Nutzen und Aktualität prüfen.' }
  }
  if ($Relative.StartsWith('docs/')) {
    return @{ Status='REVIEW'; Confidence='MEDIUM'; Reason='Dokumentation ohne eindeutiges Aktiv-/Archiv-Signal; Inhalt prüfen.' }
  }
  return @{ Status='REVIEW'; Confidence='LOW'; Reason='Keine sichere automatische Klassifikation.' }
}

$files = Get-ChildItem -Path $Root -Recurse -File -Force | ForEach-Object {
  $rel = Get-RelativePath $_.FullName
  if (-not (Test-Skipped $rel)) {
    $classification = Classify-File $rel $_
    [PSCustomObject]@{
      Path = $rel
      Status = $classification.Status
      Confidence = $classification.Confidence
      Reason = $classification.Reason
      SizeBytes = $_.Length
      Modified = $_.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss')
    }
  }
}

$files = @($files | Sort-Object Status, Path)
$summary = $files | Group-Object Status | Sort-Object Name | ForEach-Object {
  [PSCustomObject]@{ Status=$_.Name; Count=$_.Count }
}

$csvPath = Join-Path $ReportDir 'cleanup_inventory.csv'
$jsonPath = Join-Path $ReportDir 'cleanup_inventory.json'
$mdPath = Join-Path $ReportDir 'cleanup_report.md'
$files | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
$files | ConvertTo-Json -Depth 4 | Set-Content -Path $jsonPath -Encoding UTF8

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add('# VADAFOK Studio – Cleanup Analyzer 2.19 RC2')
$lines.Add('')
$lines.Add('> Diese Analyse hat keine Projektdateien verschoben, umbenannt oder gelöscht.')
$lines.Add('')
$lines.Add('## Zusammenfassung')
$lines.Add('')
$lines.Add('| Status | Anzahl |')
$lines.Add('|---|---:|')
foreach ($row in $summary) { $lines.Add("| $($row.Status) | $($row.Count) |") }
$lines.Add('')
$lines.Add('## Bedeutung')
$lines.Add('')
$lines.Add('- **ACTIVE:** mit hoher Sicherheit aktiv; nicht archivieren.')
$lines.Add('- **ARCHIVE_CANDIDATE:** wahrscheinlich historische Test-/Release-Dokumentation; Inhalt bleibt zu erhalten.')
$lines.Add('- **REMOVE_CANDIDATE:** wahrscheinlich generiert oder entbehrlich; vor Entfernen bestätigen.')
$lines.Add('- **REVIEW:** nicht automatisch entscheiden; gezielt prüfen.')
$lines.Add('')
foreach ($status in @('ARCHIVE_CANDIDATE','REMOVE_CANDIDATE','REVIEW','ACTIVE')) {
  $group = @($files | Where-Object Status -eq $status)
  $lines.Add("## $status ($($group.Count))")
  $lines.Add('')
  $lines.Add('| Datei | Sicherheit | Begründung |')
  $lines.Add('|---|---|---|')
  foreach ($item in $group) {
    $safePath = $item.Path.Replace('|','\|')
    $safeReason = $item.Reason.Replace('|','\|')
    $lines.Add("| `$safePath` | $($item.Confidence) | $safeReason |")
  }
  $lines.Add('')
}
$lines.Add('## Nächster Schritt')
$lines.Add('')
$lines.Add('Sende vorzugsweise nur `cleanup_report.md`. Daraus kann ein kontrolliertes Archivpaket erstellt werden. Es sind keine Einzel-Screenshots nötig.')
$lines | Set-Content -Path $mdPath -Encoding UTF8

Write-Host ''
Write-Host 'Cleanup analysis complete.' -ForegroundColor Green
Write-Host 'No project files were moved or deleted.' -ForegroundColor Green
Write-Host "Report: $mdPath"
Write-Host "CSV:    $csvPath"
Write-Host "JSON:   $jsonPath"
exit 0
