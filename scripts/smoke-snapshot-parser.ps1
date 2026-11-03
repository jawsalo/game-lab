[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$JavaExecutable,

    [Parameter(Mandatory = $true)]
    [string]$GdEditJar,

    [Parameter(Mandatory = $true)]
    [string]$CharacterSave,

    [Parameter(Mandatory = $true)]
    [string]$SharedStash
)

$ErrorActionPreference = 'Stop'

foreach ($path in @($JavaExecutable, $GdEditJar, $CharacterSave, $SharedStash)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw 'A required local file was not found.'
    }
}

$workerSource = (Resolve-Path (Join-Path $PSScriptRoot '..\apps\parser-worker\src')).Path
$classPath = "$GdEditJar;$workerSource"

function Invoke-ReadOnlySnapshotParse {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('character', 'sharedStash')]
        [string]$SourceType,

        [Parameter(Mandatory = $true)]
        [string]$SavePath
    )

    $javaArgs = @(
        '-Xms32m',
        '-Xmx384m',
        '-Djna.nosys=true',
        '--enable-native-access=ALL-UNNAMED',
        '-cp',
        $classPath,
        'clojure.main',
        '-m',
        'game-lab.snapshot-worker',
        $SourceType,
        $SavePath
    )

    $outputLines = & $JavaExecutable @javaArgs 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw 'The read-only parser could not read one of the selected files.'
    }

    try {
        $document = ($outputLines -join [Environment]::NewLine) | ConvertFrom-Json -ErrorAction Stop
    } catch {
        throw 'The read-only parser returned an invalid summary.'
    }

    $itemCount = 0
    if ($SourceType -eq 'character') {
        $formatVersion = [int]$document.'meta-fileinfo'.'data-version'
        foreach ($item in @($document.equipment)) {
            if ($item.basename) { $itemCount++ }
        }
        foreach ($sack in @($document.'inventory-sacks')) {
            foreach ($item in @($sack.'inventory-items')) {
                if ($item.basename) { $itemCount++ }
            }
        }
        foreach ($tab in @($document.stashes)) {
            foreach ($item in @($tab.items)) {
                if ($item.basename) { $itemCount++ }
            }
        }
    } else {
        $formatVersion = [int]$document.version
        foreach ($tab in @($document.stash)) {
            foreach ($item in @($tab.'inventory-items')) {
                if ($item.basename) { $itemCount++ }
            }
        }
    }

    [pscustomobject]@{
        SourceType    = $SourceType
        FormatVersion = $formatVersion
        ItemCount     = $itemCount
    }
}

$characterSummary = Invoke-ReadOnlySnapshotParse -SourceType character -SavePath $CharacterSave
$stashSummary = Invoke-ReadOnlySnapshotParse -SourceType sharedStash -SavePath $SharedStash

$characterSummary
$stashSummary
