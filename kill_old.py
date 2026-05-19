import subprocess, os, sys

# Show running python processes
r = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     'Get-Process | Where-Object { $_.Name -like "*python*" } | Select-Object Id,Name,Path | Format-Table -AutoSize'],
    capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
)
print("Running Python processes:")
print(r.stdout)

# Kill all pythonw.exe processes (autostart old instance)
r2 = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     'Get-Process -Name "pythonw" -ErrorAction SilentlyContinue | Stop-Process -Force'],
    capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
)
print("Killed pythonw.exe instances (if any):", r2.returncode)
