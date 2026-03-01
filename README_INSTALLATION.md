# skidcleaner - Installation Guide

## 🚀 Quick Start (Recommended)

### Option 1: PowerShell Installer (Windows)
```powershell
# Open PowerShell as Administrator and run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\install_and_launch.ps1
```

### Option 2: Manual Installation
1. Install Python 3.11+ from https://python.org
2. Install dependencies: `pip install requests tqdm pyuac`
3. Open `config_gui.html` in your browser

## 📋 What This Installer Does

The `install_and_launch.ps1` script automatically:
- ✅ Checks for existing Python installation
- ✅ Downloads Python 3.11.9 if needed
- ✅ Installs required packages (requests, tqdm, pyuac)
- ✅ Launches the configuration GUI in your browser
- ✅ Provides detailed progress feedback

## 🔒 Security Information

- **Source**: This installer is part of the official skidcleaner project
- **Repository**: https://github.com/midinterlude/skidcleaner
- **Purpose**: Automated setup for the skidcleaner configuration tool
- **No data collection**: The installer only downloads Python packages
- **Open source**: All scripts are visible and auditable

## 🛡️ Verification

To verify the installer is legitimate:
1. Check the source code in the scripts
2. Compare with the GitHub repository
3. Scan with antivirus if desired
4. Only download from official sources

## 📁 Files Included

- `install_and_launch.ps1` - Main installer (PowerShell)
- `install_and_launch.bat` - Alternative installer (Batch)
- `config_gui.html` - Configuration GUI
- `README_INSTALLATION.md` - This file

## ❓ Troubleshooting

### "Script is disabled" Error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Cannot be loaded because running scripts is disabled"
Right-click the PowerShell file → "Run with PowerShell"

### Python Installation Fails
- Run as Administrator
- Check internet connection
- Install Python manually from python.org

## 🆘 Support

If you encounter issues:
1. Check the GitHub repository for updates
2. Verify you have the latest version
3. Report issues on GitHub

---

**skidcleaner** - Advanced Roblox cleaning tool
https://github.com/midinterlude/skidcleaner
