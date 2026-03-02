# PowerShell shell integration hook for this repo.
#
# Usage:
#  1. Source this file from your PowerShell profile, or run it in the workspace session:
#       .\shell_hook.ps1
#  2. Use the `track` function to run commands that should be detected and executed.
#       track "buy 100 AAPL at 150"
#
# The hook calls the project's `cli_detect.py` to detect trading commands and
# prints a JSON detection result before optionally running the command.

function track {
    param(
        [Parameter(Mandatory=$true, ValueFromRemainingArguments=$true)]
        [string[]]$CmdParts,
        [switch]$Run
    )

    $cmd = $CmdParts -join ' '
    $py = "py"
    $script = Join-Path (Get-Location) 'cli_detect.py'
    if (-not (Test-Path $script)) {
        Write-Error "cli_detect.py not found in current folder. cd to repository root."
        return
    }

    $result = & $py $script -- $cmd 2>$null
    if ($LASTEXITCODE -ne 0) {
        # try without extra --
        $result = & $py $script $cmd 2>$null
    }

    if ($result) {
        Write-Host "[track] detection: $result"
    } else {
        Write-Host "[track] no commands detected"
    }

    if ($Run.IsPresent) {
        Write-Host "[track] executing: $cmd"
        Invoke-Expression $cmd
    }
}

Set-Variable -Name __shell_integration_hook_loaded -Value $true -Scope Global -Option ReadOnly
