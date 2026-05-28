param(
    [string]$MatlabPath,
    [string]$Command,
    [string]$File,
    [string]$WorkDir,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if (-not $Command -and -not $File) {
    throw "Provide either -Command or -File."
}

if ($Command -and $File) {
    throw "Use only one of -Command or -File."
}

if (-not $MatlabPath) {
    $cmd = Get-Command matlab -ErrorAction SilentlyContinue
    if ($cmd) {
        $MatlabPath = $cmd.Source
    }
}

if (-not $MatlabPath) {
    $candidates = @((
        @(
            "C:\Program Files\MATLAB",
            "D:\Program Files\MATLAB"
        ) | Where-Object { Test-Path $_ } | ForEach-Object {
            Get-ChildItem $_ -Directory | Sort-Object Name -Descending | ForEach-Object {
                Join-Path $_.FullName "bin\matlab.exe"
            }
        } | Where-Object { Test-Path $_ }
    ))

    if ($candidates.Count -gt 0) {
        $MatlabPath = $candidates[0]
    }
}

if (-not $MatlabPath) {
    throw "MATLAB executable not found. Pass -MatlabPath or add matlab to PATH."
}

if ($File) {
    $resolvedFile = Resolve-Path -LiteralPath $File
    $matlabCommand = "run('$($resolvedFile.Path.Replace("'", "''"))')"
} else {
    $matlabCommand = $Command
}

$arguments = @("-batch", $matlabCommand)

if ($DryRun) {
    [PSCustomObject]@{
        MatlabPath = $MatlabPath
        WorkDir = $WorkDir
        Arguments = $arguments
    } | ConvertTo-Json -Depth 4
    exit 0
}

$startInfo = @{
    FilePath = $MatlabPath
    ArgumentList = $arguments
    Wait = $true
    NoNewWindow = $true
    PassThru = $true
}

if ($WorkDir) {
    $startInfo.WorkingDirectory = (Resolve-Path -LiteralPath $WorkDir).Path
}

$process = Start-Process @startInfo
exit $process.ExitCode
