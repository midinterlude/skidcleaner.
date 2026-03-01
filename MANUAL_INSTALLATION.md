# skidcleaner - Manual Installation Guide

## 🔒 For Security-Conscious Users

This guide provides step-by-step manual installation with full transparency and control over what gets installed on your system.

---

## 📋 Prerequisites

- Windows 10 or later
- Administrator access (recommended for Python installation)
- Internet connection for package downloads

---

## 🐍 Step 1: Install Python

### Option A: Official Website (Recommended)
1. Visit https://www.python.org/downloads/
2. Download **Python 3.11.9** (or latest 3.11.x version)
3. Run the installer
4. **IMPORTANT**: Check these options:
   - ✅ **Add Python to PATH**
   - ✅ **Install for all users** (if admin)
   - ❌ **Install launcher for all users** (optional)
5. Click "Install Now"

### Option B: Microsoft Store (Windows 10/11)
1. Open Microsoft Store
2. Search for "Python 3.11"
3. Click "Install"
4. Note: Store version may have PATH limitations

### Option C: Chocolatey (Advanced)
```powershell
# If you have Chocolatey installed:
choco install python
```

### Verify Installation
Open Command Prompt and run:
```cmd
python --version
pip --version
```

You should see version numbers (e.g., Python 3.11.9).

---

## 📦 Step 2: Install Required Packages

Open Command Prompt or PowerShell and run:

```cmd
pip install requests tqdm pyuac
```

### What Each Package Does:
- **`requests`** - HTTP library for downloading files
- **`tqdm`** - Progress bar library
- **`pyuac`** - User Account Control helper (Windows elevation)

### Verify Packages
```cmd
pip list | findstr "requests tqdm pyuac"
```

---

## 🌐 Step 3: Launch the Configuration GUI

### Option A: Double-Click (Easiest)
1. Navigate to the skidcleaner folder
2. Double-click `config_gui.html`
3. It will open in your default browser

### Option B: Command Line
```cmd
# From the skidcleaner directory:
start config_gui.html
```

### Option C: Specific Browser
```cmd
# Edge:
msedge config_gui.html

# Chrome:
chrome config_gui.html

# Firefox:
firefox config_gui.html
```

---

## ✅ Step 4: Verify Everything Works

1. The GUI should open in your browser
2. You should see the skidcleaner configuration interface
3. Try toggling a few settings to ensure functionality
4. Click "Save Only" to test script generation

---

## 🔧 Troubleshooting

### "Python is not recognized" Error
**Solution**: Python wasn't added to PATH during installation
1. Reinstall Python and ensure "Add Python to PATH" is checked
2. Or add Python manually to Windows PATH

### "pip is not recognized" Error
**Solution**: PATH issue or pip not installed
1. Try `python -m pip --version`
2. If that works, use `python -m pip install` instead of `pip install`

### GUI Won't Open
**Solutions**:
1. Try a different browser
2. Check that `config_gui.html` exists
3. Ensure file isn't blocked by Windows:
   ```cmd
   right-click config_gui.html → Properties → Unblock
   ```

### Package Installation Fails
**Solutions**:
1. Run as Administrator
2. Try different package index:
   ```cmd
   pip install -i https://pypi.org/simple/ requests tqdm pyuac
   ```
3. Upgrade pip first:
   ```cmd
   python -m pip install --upgrade pip
   ```

---

## 🎯 What You've Installed

### Python Components
- **Python 3.11.x** - Core programming language
- **pip** - Package manager
- **3 Python packages** (~5MB total)

### skidcleaner Files
- **`config_gui.html`** - Web-based configuration interface (~50KB)
- **Generated scripts** - Only when you click "Save"

### Total Installation Size
- **Python**: ~100MB
- **Packages**: ~5MB
- **skidcleaner**: ~50KB
- **Total**: ~105MB

---

## 🔍 Security Verification

### Verify Python Installation
1. Check installer source: https://python.org
2. Verify digital signature on installer
3. Scan with antivirus if desired

### Verify Package Sources
```cmd
pip show requests
pip show tqdm  
pip show pyuac
```
Each should show "Home-page: https://pypi.org/project/..."

### Verify skidcleaner Files
1. Open `config_gui.html` in a text editor
2. Review the code (it's just HTML/CSS/JavaScript)
3. No executable code, runs in browser sandbox

---

## 🗑️ Uninstallation

If you want to remove everything:

### Remove Python Packages
```cmd
pip uninstall requests tqdm pyuac
```

### Remove Python
- Use "Add or Remove Programs" in Windows Settings
- Search for "Python 3.11"
- Click "Uninstall"

### Remove skidcleaner
- Delete the skidcleaner folder
- No registry entries or system modifications

---

## 📞 Need Help?

- **GitHub Repository**: https://github.com/midinterlude/skidcleaner
- **Create an Issue**: Report problems on GitHub
- **Check README**: Look for additional documentation

---

## 🎉 Next Steps

Once everything is installed:

1. **Configure Settings**: Use the GUI to set your cleaning preferences
2. **Generate Script**: Click "Save Only" or "Save and Run"
3. **Test Script**: Run the generated Python script
4. **Share**: Distribute the generated script to others

**Congratulations! You now have full control over your skidcleaner installation.** 🔒✨
