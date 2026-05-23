$ErrorActionPreference = "Stop"

Get-ScheduledTask -TaskName "SnapMediaToggle" | Select-Object TaskName, State
Get-ScheduledTaskInfo -TaskName "SnapMediaToggle" | Select-Object LastRunTime, LastTaskResult, NextRunTime
