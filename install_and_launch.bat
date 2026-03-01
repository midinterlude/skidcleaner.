@echo off
setlocal enabledelayedexpansion

echo ========================================
echo skidcleaner Auto-Installer
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Downloading Python installer...
    
    :: Download Python installer
    echo Downloading Python 3.11...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python-installer.exe'"
    
    echo Installing Python...
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    :: Wait for installation
    timeout /t 10 /nobreak >nul
    
    :: Clean up installer
    del python-installer.exe
    
    echo Python installation completed!
) else (
    echo Python is already installed.
)

:: Refresh PATH
set PATH=%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\Scripts;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311

:: Install required packages
echo.
echo Installing required packages...
pip install requests tqdm pyuac

:: Check if GUI file exists
set "GUI_FILE=%~dp0config_gui.html"
if not exist "%GUI_FILE%" (
    echo ERROR: config_gui.html not found in the same directory!
    echo Please make sure config_gui.html is in the same folder as this installer.
    pause
    exit /b 1
)

:: Launch the GUI
echo.
echo Launching skidcleaner Configuration GUI...
echo.

:: Open the HTML file in default browser
start "" "%GUI_FILE%"

echo.
echo ========================================
echo skidcleaner GUI launched successfully!
echo ========================================
echo.
echo The configuration GUI should now be open in your default browser.
echo You can configure your cleaning settings and generate custom scripts.
echo.
pause
