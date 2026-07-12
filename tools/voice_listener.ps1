param(
    [string]$Culture = ""
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech

if ([string]::IsNullOrWhiteSpace($Culture)) {
    $recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
} else {
    $cultureInfo = New-Object System.Globalization.CultureInfo($Culture)
    $recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine($cultureInfo)
}

$grammar = New-Object System.Speech.Recognition.DictationGrammar
$recognizer.LoadGrammar($grammar)
$recognizer.SetInputToDefaultAudioDevice()

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::Out.WriteLine("__READY__")
[Console]::Out.Flush()

while ($true) {
    try {
        $result = $recognizer.Recognize()
        if ($null -ne $result -and -not [string]::IsNullOrWhiteSpace($result.Text)) {
            [Console]::Out.WriteLine($result.Text)
            [Console]::Out.Flush()
        }
    } catch {
        [Console]::Error.WriteLine($_.Exception.Message)
        [Console]::Error.Flush()
        Start-Sleep -Milliseconds 350
    }
}
