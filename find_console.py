import subprocess

# Find scheduled tasks with powershell
script = r"""
$tasks = Get-ScheduledTask | Where-Object {
    $_.Actions | Where-Object { $_.Execute -like '*powershell*' -or $_.Execute -like '*pwsh*' -or $_.Execute -like '*python*' }
}
foreach ($t in $tasks) {
    foreach ($a in $t.Actions) {
        Write-Host "TASK:" $t.TaskName
        Write-Host "  Path:" $t.TaskPath
        Write-Host "  Exe:" $a.Execute
        Write-Host "  Args:" $a.Arguments
        Write-Host "---"
    }
}
"""

r = subprocess.run(
    ["powershell", "-NonInteractive", "-NoProfile", "-Command", script],
    capture_output=True, text=True, timeout=20,
    creationflags=subprocess.CREATE_NO_WINDOW
)
print("=== Scheduled Tasks with PowerShell/Python ===")
print(r.stdout if r.stdout.strip() else "(none found)")

# Check startup registry
script2 = r"""
$paths = @(
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run",
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run"
)
foreach ($p in $paths) {
    Write-Host "=== $p ==="
    Get-ItemProperty $p | Format-List
}
"""
r2 = subprocess.run(
    ["powershell", "-NonInteractive", "-NoProfile", "-Command", script2],
    capture_output=True, text=True, timeout=10,
    creationflags=subprocess.CREATE_NO_WINDOW
)
print("\n=== Startup Registry ===")
print(r2.stdout)
