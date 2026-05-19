@echo off
cd /d "%~dp0"
echo [BatteryLife] Collecting PyInstaller...

set PIB=%APPDATA%\Python\Python314\Scripts\pyinstaller.exe
if not exist "%PIB%" (
    for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)"') do set PYEXE=%%i
    for %%i in ("%PYEXE%") do set PYDIR=%%~dpi
    set PIB=%PYDIR%Scripts\pyinstaller.exe
)

echo [BatteryLife] Building...
"%PIB%" --onefile --noconsole --name BatteryLife ^
  --hidden-import=pystray._win32 ^
  --hidden-import=pythoncom ^
  --hidden-import=wmi ^
  --hidden-import=pywintypes ^
  --hidden-import=win32com.client ^
  --hidden-import=win32api ^
  --hidden-import=win32con ^
  --collect-all=wmi ^
  main.py

if errorlevel 1 (
    echo [BatteryLife] BUILD FAILED
    pause
    exit /b 1
)

copy /Y dist\BatteryLife.exe .\BatteryLife.exe
echo [BatteryLife] Done ^> BatteryLife.exe
