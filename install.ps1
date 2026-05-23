$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$VenvPythonw = Join-Path $ProjectRoot ".venv\Scripts\pythonw.exe"
$TaskName = "SnapMediaToggle"
$ScriptPath = Join-Path $ProjectRoot "snap_toggle.py"
$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -like "*$ScriptPath*" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

if (-not (Test-Path -LiteralPath $VenvPython)) {
    python -m venv (Join-Path $ProjectRoot ".venv")
}

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
& $VenvPython $ScriptPath init-config

$Action = New-ScheduledTaskAction -Execute $VenvPythonw -Argument "`"$ScriptPath`" listen" -WorkingDirectory $ProjectRoot
$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $CurrentUser
$Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description "Toggle media playback when a finger snap is detected." -Force | Out-Null
Start-ScheduledTask -TaskName $TaskName

Write-Output "Installed and started scheduled task: $TaskName"
