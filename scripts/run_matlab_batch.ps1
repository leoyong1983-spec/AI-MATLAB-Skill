param(
    [string]$MatlabPath,
    [string]$Command,
    [string]$File,
    [string]$WorkDir,
    [switch]$SmokeTest,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$routeCount = 0
if ($Command) { $routeCount += 1 }
if ($File) { $routeCount += 1 }
if ($SmokeTest) { $routeCount += 1 }

if ($routeCount -eq 0) {
    throw "Provide -Command, -File, or -SmokeTest."
}

if ($routeCount -gt 1) {
    throw "Use only one of -Command, -File, or -SmokeTest."
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

if ($SmokeTest) {
    $matlabCommand = "disp(matlabroot); disp(version)"
} elseif ($File) {
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

if ($WorkDir) {
    Push-Location -LiteralPath (Resolve-Path -LiteralPath $WorkDir).Path
}

try {
    & $MatlabPath @arguments
    $exitCode = $LASTEXITCODE
} finally {
    if ($WorkDir) {
        Pop-Location
    }
}

if ($null -eq $exitCode) {
    exit 0
}

exit $exitCode
