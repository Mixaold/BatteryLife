import subprocess

script = r"""
$d = Get-PnpDevice | Where-Object { $_.FriendlyName -like '*WH-1000XM4*' }
$d | Select-Object FriendlyName, Status, InstanceId | Format-List
foreach ($dev in $d) {
    $p = Get-PnpDeviceProperty -InstanceId $dev.InstanceId -KeyName '{104EA319-6EE2-4701-BD47-8DDBF425BBE5} 2' -ErrorAction SilentlyContinue
    if ($p) { Write-Host "Battery for" $dev.FriendlyName ":" $p.Data }
    else { Write-Host "No battery property for" $dev.FriendlyName }
}
"""

r = subprocess.run(
    ["powershell", "-NonInteractive", "-NoProfile", "-Command", script],
    capture_output=True, text=True, timeout=15
)
print("STDOUT:", r.stdout)
print("STDERR:", r.stderr[:300] if r.stderr else "")
