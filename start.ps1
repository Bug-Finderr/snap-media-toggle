$ErrorActionPreference = "Stop"

Start-ScheduledTask -TaskName "SnapMediaToggle"
Write-Output "Started SnapMediaToggle"
