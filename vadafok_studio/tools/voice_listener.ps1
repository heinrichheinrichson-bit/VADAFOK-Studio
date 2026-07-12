param([string]$Culture = "")

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

try {
    Add-Type -AssemblyName System.Speech

    $recognizer = $null

    if (-not [string]::IsNullOrWhiteSpace($Culture)) {
        try {
            $cultureInfo = New-Object System.Globalization.CultureInfo($Culture)
            $recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine($cultureInfo)
        } catch {
            [Console]::Out.WriteLine("__WARN__|Culture '$Culture' unavailable. Falling back to Windows default.")
            [Console]::Out.Flush()
        }
    }

    if ($null -eq $recognizer) {
        $recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
    }

    $choices = New-Object System.Speech.Recognition.Choices
    $choices.Add("live card")
    $choices.Add("Live Card")

    $builder = New-Object System.Speech.Recognition.GrammarBuilder
    $builder.Append($choices)

    $grammar = New-Object System.Speech.Recognition.Grammar($builder)
    $recognizer.LoadGrammar($grammar)
    $recognizer.SetInputToDefaultAudioDevice()

    [Console]::Out.WriteLine("__READY__")
    [Console]::Out.Flush()

    while ($true) {
        $result = $recognizer.Recognize()
        if ($null -ne $result -and -not [string]::IsNullOrWhiteSpace($result.Text)) {
            [Console]::Out.WriteLine("__HEARD__|" + $result.Text)
            [Console]::Out.Flush()
        }
    }
}
catch {
    [Console]::Out.WriteLine("__ERROR__|" + $_.Exception.Message)
    [Console]::Out.Flush()
    exit 1
}
