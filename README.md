# Snap Media Toggle

Listens to the default microphone and sends the Windows media play/pause key when it detects a finger snap.

## Install

```powershell
.\install.ps1
```

This creates `.venv`, installs dependencies, creates `config.json`, registers the `SnapMediaToggle` scheduled task for your logon, and starts it.

## Commands

```powershell
.\.venv\Scripts\python.exe .\snap_toggle.py dry-run
.\.venv\Scripts\python.exe .\snap_toggle.py test-key
.\.venv\Scripts\python.exe .\snap_toggle.py devices
.\status.ps1
.\stop.ps1
.\start.ps1
.\uninstall.ps1
```

Use `dry-run` first if you want to tune sensitivity. Logs are written to `logs\snap-media-toggle.log`.
