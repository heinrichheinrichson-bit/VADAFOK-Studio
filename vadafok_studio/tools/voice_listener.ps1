param([string]$Culture = "")

$ErrorActionPreference = "Stop"
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

function Write-VoiceLine([string]$Text) {
    [Console]::Out.WriteLine($Text)
    [Console]::Out.Flush()
}

function Get-ErrorText($ErrorRecord) {
    if ($null -eq $ErrorRecord) { return "Unknown voice listener error." }
    $message = $ErrorRecord.Exception.Message
    if ([string]::IsNullOrWhiteSpace($message)) { $message = [string]$ErrorRecord }
    return ($message -replace "[\r\n]+", " ").Trim()
}

$recognizer = $null
try {
    Add-Type -AssemblyName System.Speech

    $installed = @(
        [System.Speech.Recognition.SpeechRecognitionEngine]::InstalledRecognizers()
    )
    if ($installed.Count -eq 0) {
        throw "No Windows desktop speech recognizer is installed."
    }

    if ([string]::IsNullOrWhiteSpace($Culture)) {
        $selected = $installed | Select-Object -First 1
    }
    else {
        $selected = $installed | Where-Object {
            $_.Culture.Name -ieq $Culture
        } | Select-Object -First 1
    }

    if ($null -eq $selected) {
        $available = ($installed | ForEach-Object { $_.Culture.Name }) -join ", "
        throw "Recognizer '$Culture' is not installed. Available: $available"
    }

    $recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine($selected)

    # High-priority grammar for the same three core commands in every culture.
    # Python performs additional fuzzy matching if Windows returns a near miss.
    $choices = New-Object System.Speech.Recognition.Choices
    $commandPhrases = @(
        "live card",
        "Live Card",
        "vadafok show",
        "Vadafok Show",
        "vadafok reset",
        "Vadafok Reset",
        "vadafok stop",
        "Vadafok Stop",
        "vadafok quick card",
        "Vadafok Quick Card",
        "vadafok one",
        "Vadafok One",
        "vadafok eins",
        "Vadafok Eins",
        "vadafok two",
        "Vadafok Two",
        "vadafok zwei",
        "Vadafok Zwei",
        "vadafok three",
        "Vadafok Three",
        "vadafok drei",
        "Vadafok Drei",
        "vadafok text",
        "Vadafok Text",
        "vadafok back",
        "Vadafok Back"
    )
    foreach ($phrase in $commandPhrases) { [void]$choices.Add($phrase) }

    $builder = New-Object System.Speech.Recognition.GrammarBuilder
    $builder.Culture = $selected.Culture
    $builder.Append($choices)

    $commandGrammar = New-Object System.Speech.Recognition.Grammar($builder)
    $commandGrammar.Name = "command"
    $commandGrammar.Priority = 127
    $commandGrammar.Weight = 1.0
    $recognizer.LoadGrammar($commandGrammar)

    # TEST08: System.Speech is command-only. Free dictation is handled by
    # local Whisper in Python for substantially better DE/EN transcription.

    $recognizer.InitialSilenceTimeout = [TimeSpan]::FromSeconds(30)
    $recognizer.BabbleTimeout = [TimeSpan]::FromSeconds(4)
    $recognizer.EndSilenceTimeout = [TimeSpan]::FromMilliseconds(900)
    $recognizer.EndSilenceTimeoutAmbiguous = [TimeSpan]::FromMilliseconds(1200)
    $recognizer.SetInputToDefaultAudioDevice()

    Write-VoiceLine (
        "__READY__|" + $selected.Culture.Name + "|" + $selected.Description
    )

    while ($true) {
        try {
            $result = $recognizer.Recognize()
            if ($null -eq $result) { continue }
            if ([string]::IsNullOrWhiteSpace($result.Text)) { continue }

            $confidence = [Math]::Round($result.Confidence, 3).ToString(
                [System.Globalization.CultureInfo]::InvariantCulture
            )
            $grammarKind = "unknown"
            if ($null -ne $result.Grammar -and
                -not [string]::IsNullOrWhiteSpace($result.Grammar.Name)) {
                $grammarKind = $result.Grammar.Name
            }

            Write-VoiceLine (
                "__HEARD__|" + $confidence + "|" + $grammarKind + "|" + $result.Text
            )
        }
        catch [System.TimeoutException] {
            continue
        }
        catch {
            Write-VoiceLine (
                "__WARN__|Recognition recovered: " + (Get-ErrorText $_)
            )
            Start-Sleep -Milliseconds 250
        }
    }
}
catch {
    Write-VoiceLine ("__ERROR__|" + (Get-ErrorText $_))
    exit 1
}
finally {
    if ($null -ne $recognizer) {
        try { $recognizer.Dispose() } catch { }
    }
}
