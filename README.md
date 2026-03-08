# ordl-aether

Main app: `aether-system/`

## Security Gate

Before push:

```bash
python scripts/secret_scan.py
```

Optional local pre-push hook install (PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_pre_push_hook.ps1
```
