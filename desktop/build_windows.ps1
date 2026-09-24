$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
python -m pip install --upgrade pip pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed --name "NEON-OS-Desktop" neon_os.py
Write-Host "Built: $PSScriptRoot\dist\NEON-OS-Desktop.exe"
