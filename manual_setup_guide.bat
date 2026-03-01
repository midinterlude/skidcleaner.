@echo off
title skidcleaner - Manual Setup Guide

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              skidcleaner - Manual Setup Guide               ║
echo ║              For Security-Conscious Users                    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo This guide will help you install skidcleaner manually.
echo You will have full control over what gets installed.
echo.
echo Press any key to continue...
pause >nul

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                      STEP 1: Install Python                   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 1. Open your web browser
echo 2. Go to: https://www.python.org/downloads/
echo 3. Download Python 3.11.9 (or latest 3.11.x)
echo 4. Run the installer
echo 5. IMPORTANT: Check "Add Python to PATH"
echo 6. Click "Install Now"
echo.
echo After installation, open Command Prompt and test:
echo    python --version
echo.
echo Press any key to continue to next step...
pause >nul

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    STEP 2: Install Packages                    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Open Command Prompt and run this command:
echo.
echo    pip install requests tqdm pyuac
echo.
echo This installs:
echo   - requests: HTTP library
echo   - tqdm: Progress bars  
echo   - pyuac: Windows UAC helper
echo.
echo Press any key to continue to next step...
pause >nul

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                      STEP 3: Launch GUI                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Double-click on: config_gui.html
echo.
echo This will open the skidcleaner configuration interface
echo in your default web browser.
echo.
echo Press any key to continue to next step...
pause >nul

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                     STEP 4: Verify Setup                        ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Test that everything works:
echo.
echo 1. The GUI should open in your browser
echo 2. Try toggling some settings
echo 3. Click "Save Only" to test script generation
echo 4. Check that a .py file is downloaded
echo.
echo Press any key to continue...
pause >nul

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                     Installation Complete!                    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ✅ Manual setup complete!
echo.
echo 📁 For detailed troubleshooting, see:
echo    MANUAL_INSTALLATION.md
echo.
echo 🔗 Project repository:
echo    https://github.com/midinterlude/skidcleaner
echo.
echo 🎮 Your skidcleaner configuration GUI is ready to use!
echo.
echo Press any key to exit...
pause >nul

echo.
echo Opening config_gui.html now...
start "" "config_gui.html"
