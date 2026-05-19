import wmi, pythoncom
pythoncom.CoInitialize()
c = wmi.WMI()
BATT_KEY = "{104EA319-6EE2-4701-BD47-8DDBF425BBE5} 2"
devs = c.query("SELECT DeviceID FROM Win32_PnPEntity WHERE Name LIKE '%WH-1000XM4%'")
for d in devs:
    did = d.DeviceID.replace("\\", "\\\\")
    props = c.query(
        f"SELECT Data FROM Win32_PnPDeviceProperty "
        f"WHERE DeviceID='{did}' AND KeyName='{BATT_KEY}'"
    )
    for p in props:
        print("DeviceID:", d.DeviceID[:50], "-> Battery:", p.Data)
pythoncom.CoUninitialize()
