$ErrorActionPreference = "Stop"

Stop-ScheduledTask -TaskName "SnapMediaToggle"
Write-Output "Stopped SnapMediaToggle"
