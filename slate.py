# ===== IMPORTS AND GLOBALS =====
import sys, subprocess, os, shutil, glob, json, stat, uuid, time, requests, threading, zipfile, urllib3, winreg, pyperclip, traceback, msvcrt, random, ctypes, sqlite3, tkinter as tk
from tqdm import tqdm

# ===== Initial Clear =====
os.system("cls")

# ===== PATHS AND CONSTANTS =====
script_dir = os.path.dirname(os.path.abspath(__file__))
slate_dir = sys._MEIPASS if hasattr(sys, "_MEIPASS") else script_dir
base_dir = os.path.dirname(sys.executable) if hasattr(sys, "_MEIPASS") else script_dir
misc_dir = os.path.join(base_dir, "misc")
cert_path = os.path.join(misc_dir, "cacert.pem")

LP = os.path.join(misc_dir, "slate.log")
PF = os.path.expandvars(r"C:\Windows\Prefetch\ROBLOX*.pf")
REGS = [r"HKCU\Software\Roblox", r"HKLM\SOFTWARE\Roblox Corporation"]
CK = os.path.expandvars(r"%appdata%\local\Roblox\Localstorage\RobloxCookies.dat")
PROCS = ["RobloxPlayerBeta.exe", "RobloxPlayerInstaller.exe"]
PATHS = [
    r"%temp%",
    r"%temp%/*",
    r"%localappdata%\Temp",
    r"%localappdata%\Roblox",
    r"%appdata%\Roblox", 
    r"%appdata%\Local\Roblox",
]
VERSION = "2.0.0"
VERSION_URL = "https://raw.githubusercontent.com/midinterlude/slate/main/version.txt"
download_url = "https://github.com/midinterlude/slate/releases/latest"

# ===== ERROR CLASSES =====
class SlateError(Exception):
    def __init__(self, message, operation=None, details=None):
        super().__init__(message)
        self.operation = operation
        self.details = details or {}


class ConfigurationError(SlateError):
    pass


class DownloadError(SlateError):
    pass


class FileOperationError(SlateError):
    pass


class ProcessError(SlateError):
    pass


class NetworkError(SlateError):
    pass


class RegistryError(SlateError):
    pass


# ===== LOGGING =====
LOG = True
OPEN_LOG = True


def log(msg, debug_only=False):

    is_progress_bar = any(
        char in msg for char in ["█", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "│"]
    )

    debug_prefix = "🔍 DEBUG: " if debug_only else ""

    if is_progress_bar:
        if "100%" in msg:
            print(msg, end="\r")
            print()
            return
        else:
            print(msg, end="\r")
            return
    elif (
        msg.endswith("downloaded and extracted")
        or msg.endswith("packages")
        or "Successfully downloaded" in msg
    ):
        print(msg)
    else:
        print(f"{debug_prefix}{msg}" if not debug_only else msg)

    if LOG and not debug_only:
        try:
            clean_msg = msg.replace("\r", "")
            if (
                "|" in clean_msg
                and "%" in clean_msg
                and any(
                    char in clean_msg
                    for char in ["█", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "│"]
                )
            ):
                return
            log_dir = os.path.dirname(LP)
            os.makedirs(log_dir, exist_ok=True)
            with open(LP, "a", encoding="utf-8") as f:
                timestamp = time.strftime("%H:%M:%S")
                log_entry = (
                    f"[{timestamp}] DEBUG: {clean_msg}"
                    if debug_only
                    else f"[{timestamp}] {clean_msg}"
                )
                f.write(log_entry + "\n")
                f.flush()
        except Exception as e:
            error_msg = f"Log write error: {e}"
            print(f"🔍 DEBUG: {error_msg}" if debug_only else error_msg)


def auto_close():
    print("=" * 51)
    print("This window will automatically close in 15 seconds.")
    print("Press Enter to close immediately...")
    print("=" * 51)

    start_time = time.time()
    delay = 15

    while time.time() - start_time < delay:
        remaining = int(delay - (time.time() - start_time))
        print(
            f"\rClosing in {remaining} seconds... (Press Enter to close)",
            end="",
            flush=True,
        )
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b"\r":
                print("\nClosing immediately...")
                break

        time.sleep(0.1)

    print("\n")


# ===== SLATE BETA INTEGRATION (UI) =====
def load_slate_settings():
    default_settings = {"show_console": True}
    
    if hasattr(sys, "_MEIPASS"):
        exe_dir = os.path.dirname(sys.executable)
        settings_path = os.path.join(exe_dir, "slatesettings.json")
    else:
        settings_path = os.path.join(script_dir, "slatesettings.json")

    if not os.path.exists(settings_path):
        log("slatesettings.json not found, using default settings.")
        return default_settings

    try:
        with open(settings_path, "r") as f:
            settings = json.load(f)
            return {**default_settings, **settings}
    except (json.JSONDecodeError, IOError) as e:
        log(f"Error reading slatesettings.json: {e}. Using default settings.")
        return default_settings

def hide_console():
    try:
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)
            log("Console hidden based on settings.")
    except Exception as e:
        log(f"Could not hide console window: {e}")

def show_completion_popup():
    try:
        MB_ICONINFORMATION = 0x00000040
        ctypes.windll.user32.MessageBoxW(0, "Slate has finished its operations", "Slate", MB_ICONINFORMATION)
    except Exception as e:
        print("\n\nSlate has finished its operations.\n")
        log(f"Could not show completion popup: {e}")

# ===== CONFIGURATION =====
def load_cfg():
    log("Loading configuration file")
    if hasattr(sys, "_MEIPASS"):
        exe_dir = os.path.dirname(sys.executable)
        config_path = os.path.join(exe_dir, "slate.config.json")
        log("🔍 DEBUG: Running as EXE, config path: " + config_path, debug_only=True)
    else:
        config_path = os.path.join(slate_dir, "slate.config.json")
        log("🔍 DEBUG: Running as script, config path: " + config_path, debug_only=True)

    if not os.path.exists(config_path):
        print("❌ Required configuration file not found: slate.config.json")
        print(
            "Please visit https://midinterlude.github.io/slate/ to get the configuration file"
        )
        print("The link has been copied to your clipboard.")

        try:
            pyperclip.copy("https://midinterlude.github.io/slate/")
        except ImportError:
            try:
                subprocess.run(
                    ["cmd", "/c", "echo https://midinterlude.github.io/slate/ | clip"],
                    shell=True,
                    capture_output=True,
                )
            except:
                print(
                    "Could not copy link to clipboard automatically. Please manually copy: https://midinterlude.github.io/slate/"
                )

        auto_close()
        sys.exit(1)

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            print(f"✅ Configuration loaded from: slate.config.json")
            return config
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        print("Please check your slate.config.json file for syntax errors.")
        log(f"🔍 DEBUG: JSON decode error: {e}", debug_only=True)
        auto_close()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading configuration file: {e}")
        log(f"🔍 DEBUG: Config load error: {e}", debug_only=True)
        auto_close()
        sys.exit(1)


def ensure_deps():
    missing = []
    for pkg in ("requests", "tqdm"):
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            print(f"Successfully installed: {', '.join(missing)}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install packages: {e}")
            print("Please install the following packages manually:")
            for pkg in missing:
                print(f"  pip install {pkg}")
            log(f"🔍 DEBUG: Package install failed: {e}", debug_only=True)
            input("Press Enter to exit...")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error during package installation: {e}")
            log(f"🔍 DEBUG: Package install error: {e}", debug_only=True)
            input("Press Enter to exit...")
            sys.exit(1)


ensure_deps()

def ensure_cert():
    if not os.path.exists(misc_dir):
        try:
            os.makedirs(misc_dir, exist_ok=True)
        except OSError:
            pass

    if not os.path.exists(cert_path):
        print("Downloading required files (cacert.pem)...")
        try:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.get("https://curl.se/ca/cacert.pem", verify=False, stream=True)
            with open(cert_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("✅ Successfully downloaded cacert.pem")
        except Exception as e:
            print(f"❌ Failed to download cacert.pem: {e}")

    if os.path.exists(cert_path):
        os.environ["SSL_CERT_FILE"] = cert_path

ensure_cert()


def validate_cfg(config):
    log("Loading configuration file")
    try:
        required_sections = [
            "general",
            "cleaning",
            "roblox",
            "tools",
            "paths",
            "processes",
            "registry",
            "advanced",
        ]
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing configuration section: {section}")
                return False
        boolean_sections = ["general", "cleaning", "roblox", "tools", "advanced"]
        for section in boolean_sections:
            for key, value in config[section].items():
                if section == "tools" and key in ["spoof_mac_mode", "spoof_mac_adapters"]:
                    continue
                if not isinstance(value, bool):
                    print(f"❌ Invalid boolean value in {section}.{key}: {value}")
                    return False
        list_sections = ["paths", "processes", "registry"]
        for section in list_sections:
            for key, value in config[section].items():
                if not isinstance(value, list):
                    print(f"❌ Invalid list value in {section}.{key}: {value}")
                    return False
                if not value:
                    print(f"⚠️  Empty list in {section}.{key}")
        print("✅ Configuration validation passed")
        os.system("cls")
        return True
    except Exception as e:
        print(f"❌ Configuration validation error: {e}")
        return False


# ===== CLEANING OPERATIONS =====
def clean_folders(paths):
    log("Starting folder cleaning")

    all_paths = []
    for pattern in paths:
        expanded = os.path.expandvars(pattern)
        matches = glob.glob(expanded)
        if not matches and not "*" in pattern and not "?" in pattern:
            if os.path.exists(expanded):
                matches = [expanded]
        if matches:
            all_paths.extend([(path, pattern) for path in matches])
    if not all_paths:
        log("  - No files or directories found to clean")
        return
    log(f"  📁 Found {len(all_paths)} items to clean")
    success_count = 0
    error_count = 0
    error_details = []
    with tqdm(
        total=len(all_paths),
        desc="Cleaning files and folders",
        unit="item",
        file=sys.stdout,
        dynamic_ncols=True,
    ) as pbar:
        sys_root = os.environ.get("SystemRoot", r"C:\Windows")
        sys_root_abs = os.path.abspath(sys_root).lower()
        protected_exact_paths = {
            os.path.abspath(os.sep).lower(),
            sys_root_abs,
            os.path.abspath(os.environ.get("ProgramFiles", r"C:\Program Files")).lower(),
            os.path.abspath(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")).lower(),
            os.path.abspath(os.environ.get("USERPROFILE", "")).lower(),
        }
        protected_filenames = {
            "ntdll.dll", "kernel32.dll", "user32.dll", "gdi32.dll",
            "explorer.exe", "winlogon.exe", "csrss.exe", "lsass.exe", "smss.exe",
            "ntoskrnl.exe"
        }

        for path, original_pattern in all_paths:
            pbar.set_description(f"Cleaning {os.path.basename(path)}")

            abs_path_lower = os.path.abspath(path).lower()
            filename_lower = os.path.basename(abs_path_lower)
            
            skip = False
            reason = ""
            if abs_path_lower in protected_exact_paths:
                skip = True
                reason = "Exact match for a protected folder"
            elif abs_path_lower.startswith(sys_root_abs + os.sep):
                skip = True
                reason = "Child of the Windows directory"
            elif filename_lower in protected_filenames:
                skip = True
                reason = "Protected system file"

            if skip:
                log(f"  🛑 SKIPPING CRITICAL PATH ({reason}): {path}")
                error_count += 1
                error_details.append(
                    {"path": path, "error": reason, "type": "protection"}
                )
                pbar.update(1)
                continue

            try:
                if os.path.isfile(path):
                    try:
                        os.remove(path)
                        log(f"  ✅ Removed file: {path}")
                        success_count += 1
                    except PermissionError as e:
                        try:
                            os.chmod(path, stat.S_IWRITE)
                            os.remove(path)
                            log(f"  ✅ Force removed file: {path}")
                            success_count += 1
                        except Exception as e2:
                            error_msg = f"Failed to remove file {path}: {e2}"
                            log(f"  ❌ {error_msg}")
                            log(f"🔍 DEBUG: File removal failed: {e2}", debug_only=True)
                            error_count += 1
                            error_details.append(
                                {"path": path, "error": str(e2), "type": "file"}
                            )
                elif os.path.isdir(path):
                    try:
                        shutil.rmtree(path)
                        log(f"  ✅ Removed directory: {path}")
                        success_count += 1
                    except PermissionError:
                        try:
                            for root, dirs, files in os.walk(path):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    try:
                                        os.chmod(file_path, stat.S_IWRITE)
                                        os.remove(file_path)
                                    except Exception as e2:
                                        log(f"Unexpected error: {e2}")
                                        pass
                                for dir in dirs:
                                    dir_path = os.path.join(root, dir)
                                    try:
                                        os.chmod(dir_path, stat.S_IWRITE)
                                    except Exception as e2:
                                        log(f"File permission error: {e2}")
                                        pass
                            shutil.rmtree(path, ignore_errors=True)
                            log(f"  ✅ Force removed directory: {path}")
                            success_count += 1
                        except Exception as e2:
                            error_msg = f"Failed to remove directory {path} even with force: {e2}"
                            log(f"  ❌ {error_msg}")
                            error_count += 1
                            error_details.append(
                                {"path": path, "error": str(e2), "type": "directory"}
                            )
                            try:
                                for item in os.listdir(path):
                                    item_path = os.path.join(path, item)
                                    try:
                                        if os.path.isfile(item_path):
                                            os.remove(item_path)
                                        elif os.path.isdir(item_path):
                                            shutil.rmtree(item_path, ignore_errors=True)
                                    except:
                                        pass
                                os.rmdir(path)
                                log(f"  ✅ Manually cleaned directory: {path}")
                                success_count += 1
                                error_count -= 1
                            except Exception as e3:
                                final_error_msg = (
                                    f"All attempts failed for {path}: {e3}"
                                )
                                log(f"  ❌ {final_error_msg}")
                                if error_details:
                                    error_details[-1]["final_error"] = str(e3)
                                    error_details[-1]["attempts"] = "multiple"
            except Exception as e:
                error_msg = f"Unexpected error cleaning {path}: {e}"
                log(f"  ❌ {error_msg}")
                error_count += 1
                error_details.append({"path": path, "error": str(e), "type": "unknown"})
            finally:
                pbar.update(1)
                sys.stdout.flush()
    log(f"  📊 Cleaning summary: {success_count} successful, {error_count} errors")
    if error_count > 0:
        log("  ⚠️  Errors encountered during cleaning:")
        for i, detail in enumerate(error_details[:5], 1):
            log(f"     {i}. {detail['path']} ({detail['type']}): {detail['error']}")
        if len(error_details) > 5:
            log(f"     ... and {len(error_details) - 5} more errors")
        if error_count > len(all_paths) * 0.5:
            raise FileOperationError(
                f"High failure rate during folder cleaning: {error_count}/{len(all_paths)} items failed",
                operation="clean_folders",
                details={"total_items": len(all_paths), "errors": error_details},
            )


def remove_cookies():
    log("Starting cookie removal operation")
    if os.path.exists(CK):
        try:
            os.remove(CK)
            shutil.rmtree(os.path.dirname(CK), ignore_errors=True)
            log(f"  ✅ Roblox cookies removed: {CK}")
        except Exception as e:
            log(f"  ❌ Error removing Roblox cookies: {e}")
    else:
        log(f"  - Cookie file not found: {CK}")


def remove_cookies_for_host(cookie_file: str, host: str):
    if not os.path.exists(cookie_file):
        return

    conn = None
    try:
        conn = sqlite3.connect(cookie_file)
        cursor = conn.cursor()

        target_host = f'%{host}%'
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        table_name = None
        if ('cookies',) in tables:
            table_name = 'cookies'
        elif ('moz_cookies',) in tables:
            table_name = 'moz_cookies'
        
        if not table_name:
            return

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]

        host_column_name = None
        if 'host_key' in columns:
            host_column_name = 'host_key'
        elif 'host' in columns:
            host_column_name = 'host'
        
        if not host_column_name:
            return

        query_before = f"SELECT COUNT(*) FROM {table_name} WHERE {host_column_name} LIKE ?"
        cursor.execute(query_before, (target_host,))
        count_before = cursor.fetchone()[0]

        if count_before == 0:
            return

        log(f"  Found {count_before} cookies for {host} in {os.path.basename(cookie_file)}. Deleting...")

        delete_query = f"DELETE FROM {table_name} WHERE {host_column_name} LIKE ?"
        cursor.execute(delete_query, (target_host,))

        conn.commit()

        cursor.execute(query_before, (target_host,))
        count_after = cursor.fetchone()[0]
        deleted_count = count_before - count_after

        if deleted_count > 0:
            log(f"  ✅ Removed {deleted_count} cookies from {os.path.basename(cookie_file)}")
            try:
                cursor.execute("VACUUM;")
            except:
                pass
    except Exception as e:
        log(f"  ⚠️  Error processing {os.path.basename(cookie_file)}: {e}")
    finally:
        if conn:
            conn.close()

def clean_browser_cookies():
    log("Starting browser cookie cleaning")
    
    browsers = [
        ("Chrome", "chrome.exe", r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Network\Cookies"),
        ("Chrome (Legacy)", "chrome.exe", r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cookies"),
        ("Edge", "msedge.exe", r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Network\Cookies"),
        ("Opera GX", "opera.exe", r"%APPDATA%\Opera Software\Opera GX Stable\Network\Cookies"),
        ("Brave", "brave.exe", r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Network\Cookies"),
        ("Zen Browser", "zen.exe", r"%APPDATA%\Zen\Profiles\*\cookies.sqlite"),
        ("Zen Browser (Alt)", "zen.exe", r"%APPDATA%\zen-browser\Profiles\*\cookies.sqlite"),
        ("Firefox", "firefox.exe", r"%APPDATA%\Mozilla\Firefox\Profiles\*.default-release\cookies.sqlite"),
        ("Firefox (All Profiles)", "firefox.exe", r"%APPDATA%\Mozilla\Firefox\Profiles\*.default*\cookies.sqlite"),
    ]

    procs_to_kill = set(b[1] for b in browsers)
    for proc in procs_to_kill:
        run_cmd(["taskkill", "/f", "/im", proc], capture_output=True)

    host_to_remove = "roblox.com"

    for name, _, path_pattern in browsers:
        expanded_pattern = os.path.expandvars(path_pattern)
        files = glob.glob(expanded_pattern)
        
        if not files:
            continue
            
        for file_path in files:
            remove_cookies_for_host(file_path, host_to_remove)


# ===== NETWORK OPERATIONS =====
def gen_mac():
    log("Generating random MAC address")
    mac_bytes = [0x02] + [random.randint(0, 255) for _ in range(5)]
    return "".join(f"{byte:02X}" for byte in mac_bytes)


def list_adapters():
    log("Listing network adapters")
    try:

        adapters = []
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}",
        ) as class_key:
            for i in range(10000):

                try:
                    subkey_name = f"{i:04d}"
                    with winreg.OpenKey(class_key, subkey_name) as adapter_key:
                        try:
                            driver_desc = winreg.QueryValueEx(
                                adapter_key, "DriverDesc"
                            )[0]
                            net_cfg_instance_id = winreg.QueryValueEx(
                                adapter_key, "NetCfgInstanceId"
                            )[0]

                            try:
                                connection_path = f"SYSTEM\\CurrentControlSet\\Control\\Network\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}\\{net_cfg_instance_id}\\Connection"
                                with winreg.OpenKey(
                                    winreg.HKEY_LOCAL_MACHINE, connection_path
                                ) as conn_key:
                                    connection_name = winreg.QueryValueEx(
                                        conn_key, "Name"
                                    )[0]
                            except:
                                connection_name = driver_desc

                            desc_lower = driver_desc.lower()
                            if not any(
                                keyword in desc_lower
                                for keyword in [
                                    "virtual",
                                    "loopback",
                                    "bluetooth",
                                    "wan miniport",
                                    "tap-windows",
                                    "pseudo",
                                    "kernel debug",
                                ]
                            ):
                                adapters.append(
                                    {
                                        "id": subkey_name,
                                        "description": driver_desc,
                                        "connection_name": connection_name,
                                    }
                                )
                        except (FileNotFoundError, OSError):
                            continue
                except FileNotFoundError:
                    break
        return adapters
    except ImportError as e:
        log(f"[!!!] winreg module not available. Cannot list network adapters: {e}")
        return []
    except Exception as e:
        log(f"[!!!] Error listing network adapters: {e}")
        log(f"Network adapter listing error: {e}")
        return []


def change_mac(adapter_id, mac_address):
    log(f"Changing MAC for adapter {adapter_id} to {mac_address}")

    try:

        path = f"SYSTEM\\CurrentControlSet\\Control\\Class\\{{4d36e972-e325-11ce-bfc1-08002be10318}}\\{adapter_id}"
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_WRITE
        ) as adapter_key:
            log(f"[>] Setting 'NetworkAddress' to '{mac_address}'")
            winreg.SetValueEx(
                adapter_key, "NetworkAddress", 0, winreg.REG_SZ, mac_address
            )
    except ImportError:
        raise Exception("winreg module not available")
    except Exception as e:
        raise Exception(f"Registry error: {e}")


def restart_adapter(connection_name):
    log(f"Restarting adapter: {connection_name}")

    log(f"[>] Disabling adapter: '{connection_name}'")
    disable_cmd = f'netsh interface set interface name="{connection_name}" admin=disable'
    disable_result = run_cmd(disable_cmd, shell=True)
    
    if disable_result is None or disable_result.returncode != 0:
        stderr = (disable_result.stderr or "").strip() if disable_result else "Command execution failed"
        if "No more data is available" in stderr:
            log(f"  ⚠️  Adapter '{connection_name}' could not be disabled (likely a virtual or protected adapter). Skipping restart.")
            return
        
        error_msg = f"Failed to disable adapter '{connection_name}'. Output: {stderr}"
        log(f"  - {error_msg}")
        raise ProcessError(error_msg, operation="disable_adapter", details={"adapter": connection_name})

    time.sleep(2)
    
    log(f"[>] Enabling adapter: '{connection_name}'")
    enable_cmd = f'netsh interface set interface name="{connection_name}" admin=enable'
    enable_result = run_cmd(enable_cmd, shell=True)

    if enable_result is None or enable_result.returncode != 0:
        stderr = (enable_result.stderr or "").strip() if enable_result else "Command execution failed"
        if "No more data is available" in stderr:
            log(f"  ⚠️  Adapter '{connection_name}' could not be re-enabled. A manual restart might be needed.")
            return

        error_msg = f"Failed to enable adapter '{connection_name}'. Output: {stderr}"
        log(f"  - {error_msg}")
        raise ProcessError(error_msg, operation="enable_adapter", details={"adapter": connection_name})


def SpoofMAC(config, wait=True):
    log("Starting MAC spoofing operation")
    try:
        log("\n" + "=" * 41)
        log("Spoof | Based off of ByeBanAsync v2.2 | credits to: centerepic")
        log("=" * 41)

        user_profile = os.environ.get("USERPROFILE")
        if not user_profile:
            log("[!!!] Could not get USERPROFILE environment variable.")
            return
        log("\n--- MAC Address Spoofing ---")

        tools_config = config.get("tools", {})
        mode = tools_config.get("spoof_mac_mode", "all")
 
        adapters = list_adapters()
        if not adapters:
            log("[!] No suitable network adapters found to modify.")
            return

        target_adapters = []

        if mode == "manual":
            selected_adapter_names = tools_config.get("spoof_mac_adapters", [])
            if not selected_adapter_names:
                log(
                    "[!] MAC spoof mode is 'manual' but no adapters specified in 'spoof_mac_adapters' config. Skipping."
                )
                return

            log(
                f"[i] Will attempt to spoof adapters specified in config: {', '.join(selected_adapter_names)}"
            )

            for adapter in adapters:
                if (
                    adapter["connection_name"] in selected_adapter_names
                    or adapter["description"] in selected_adapter_names
                ):
                    target_adapters.append(adapter)

            if not target_adapters:
                log(
                    f"[!] None of the specified adapters could be found on this system: {', '.join(selected_adapter_names)}"
                )
                log("[i] Available adapters:")
                for i, adapter in enumerate(adapters, 1):
                    log(
                        f"  - Description: {adapter['description']}, Connection Name: '{adapter['connection_name']}'"
                    )
                return
        elif mode == "all":
            target_adapters = adapters
        else:
            log(f"[i] Invalid 'spoof_mac_mode' in config: '{mode}'. Skipping.")
            return

        for adapter in target_adapters:
            random_mac = gen_mac()
            log(
                f"\n[>] Attempting to set MAC for adapter: '{adapter['description']}' (ID: {adapter['id']})..."
            )
            try:
                change_mac(adapter["id"], random_mac)
                log("[√] Successfully updated registry for MAC address.")
                log(
                    f"[>] Attempting to restart network adapter '{adapter['connection_name']}' to apply changes..."
                )
                try:
                    restart_adapter(adapter["connection_name"])
                    log(
                        f"[√] Network adapter '{adapter['connection_name']}' restarted."
                    )
                except Exception as e:
                    log(
                        f"[!!!] Error restarting network adapter: {e}. You may need to do this manually or reboot."
                    )
                    log(f"Adapter restart error: {e}")
            except Exception as e:
                log(f"[!!!] Error changing MAC address in registry: {e}")
                log(f"Registry MAC change error: {e}")

        log("\n[...] MAC Address Spoofing completed!")
    except Exception as e:
        log(f"[!!!] Error in MAC Address Spoofing: {e}")
        log(f"MAC Address Spoofing error: {e}")

def wait_for_connection(timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            requests.get("http://www.google.com", timeout=2)
            return True
        except:
            time.sleep(0.5)
    return False

# ===== UTILITY FUNCTIONS =====
def run_cmd(cmd, capture_output=True, shell=False):
    cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
    log(f"Running command: {cmd_str}")
    try:
        if capture_output:
            result = subprocess.run(cmd, capture_output=True, text=True, shell=shell)

            if result.stdout and result.stdout.strip():
                log(f"  STDOUT: {result.stdout.strip()}")

            if result.stderr and result.stderr.strip():
                log(f"  STDERR: {result.stderr.strip()}")
        else:
            result = subprocess.run(cmd, shell=shell)
        if result.returncode == 0:
            log(f"  Command completed successfully (exit code: {result.returncode})")
        else:
            log(f"  Command exited with code: {result.returncode}")
        return result
    except Exception as e:
        log(f"Running command: {cmd_str}")
        log(f"Error running command: {e}")
        return None


def open_log():
    try:
        run_cmd(f'notepad "{LP}"', capture_output=False, shell=True)
    except Exception as e:
        print(f"Error opening log: {e}")
        log(f"Command execution error: {e}")


def launch_roblox():
    log("Starting Roblox launch operation")
    try:

        roblox_versions_dir = os.path.expandvars(r"%LOCALAPPDATA%\Roblox\Versions")
        if not os.path.exists(roblox_versions_dir):
            log("  Roblox Versions directory not found")
            return False

        version_dirs = [
            d
            for d in os.listdir(roblox_versions_dir)
            if os.path.isdir(os.path.join(roblox_versions_dir, d))
            and d.startswith("version-")
        ]
        if not version_dirs:
            log("  No Roblox version directories found")
            return False

        latest_version = sorted(version_dirs)[-1]
        roblox_exe_path = os.path.join(
            roblox_versions_dir, latest_version, "RobloxPlayerBeta.exe"
        )
        if not os.path.exists(roblox_exe_path):
            log(f"  RobloxPlayerBeta.exe not found in {latest_version}")
            return False
        log(f"  Launching Roblox from: {roblox_exe_path}")
        subprocess.Popen([roblox_exe_path])
        log("  Roblox launched successfully!")
        return True
    except Exception as e:
        log(f"  Error launching Roblox: {e}")
        log(f"Log open error: {e}")
        return False

class CustomProgressBar:
    def __init__(
        self,
        total,
        desc,
        package_index,
        total_packages,
        config=None,
    ):
        self.total = total
        self.desc = desc
        self.current = 0
        self.last_update = 0
        self.package_index = package_index
        self.total_packages = total_packages
        self.config = config

    def update(self, chunk_size):
        self.current += chunk_size
        if (
            self.current - self.last_update > 1024 * 1024
            or self.current >= self.total
        ):
            percentage = (
                (self.current / self.total) * 100
                if self.total > 0
                else 0
            )
            overall_percentage = (
                (self.package_index + (percentage / 100))
                / self.total_packages
            ) * 100

            bar_length = 50
            filled_length = int(bar_length * percentage / 100)
            bar = "█" * filled_length + "░" * (
                bar_length - filled_length
            )

            overall_filled = int(
                bar_length * overall_percentage / 100
            )
            overall_bar = "█" * overall_filled + "░" * (
                bar_length - overall_filled
            )

            print(
                f"\r{self.desc} {percentage:.1f}% |{bar}|\n\n  Total Progress {overall_percentage:.1f}% |{overall_bar}|",
                end="",
                flush=True,
            )
            if self.config:
                log(f"")
            self.last_update = self.current

    def close(self):
        bar_length = 50
        overall_percentage = (
            (self.package_index + 1) / self.total_packages
        ) * 100
        overall_filled = int(
            bar_length * overall_percentage / 100
        )
        overall_bar = "█" * overall_filled + "░" * (
            bar_length - overall_filled
        )
        print(
            f"\r{self.desc} 100.0% |{'█' * bar_length}|\n\n  Total Progress {overall_percentage:.1f}% |{overall_bar}|",
            flush=True,
        )

def get_roblox_settings(config=None):
    log("Fetching Roblox client settings")
    try:
        version_hash = ""
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        use_past_versions = (
            config and config.get("roblox", {}).get("use_past_versions", False)
            if config
            else False
        )

        if use_past_versions:
            version_url = "https://weao.xyz/api/versions/past"
            log(f"Fetching past version info from: {version_url}")
            headers = {"User-Agent": "WEAO-3PService/1.0"}
            response = requests.get(version_url, headers=headers, verify=False, timeout=15)
            response.raise_for_status()
            version_data = response.json()
            log("WEAO Past Version Response:")
            log(json.dumps(version_data, indent=2))
            if isinstance(version_data, list) and version_data:
                version_hash = version_data[-1].get("Windows", "")
                if not version_hash:
                    raise Exception("No Windows version found in last past version")
            else:
                raise Exception("Invalid response format from past versions API")
        else:
            try:
                version_url = "https://weao.xyz/api/versions/current"
                log(f"Fetching current version info from: {version_url}")
                headers = {"User-Agent": "WEAO-3PService/1.0"}
                response = requests.get(version_url, headers=headers, verify=False, timeout=10)
                response.raise_for_status()
                version_data = response.json()
                log("WEAO Current Version Response:")
                log(json.dumps(version_data, indent=2))
                version_hash = version_data.get("Windows", "")
            except (requests.RequestException, json.JSONDecodeError) as e:
                log(f"  ⚠️  Failed to fetch from weao.xyz: {e}. Falling back to official Roblox endpoint.")

            # Fallback to official Roblox endpoint if WEAO fails or doesn't provide a hash
            if not version_hash:
                version_url = "https://clientsettings.roblox.com/v1/client-version/WindowsPlayer"
                log(f"Fetching version info from official endpoint: {version_url}")
                headers = {"User-Agent": "Roblox/WinInet"}
                response = requests.get(version_url, headers=headers, verify=False, timeout=10)
                response.raise_for_status()
                version_data = response.json()
                log("Official Roblox Version Response:")
                log(json.dumps(version_data, indent=2))
                version_hash = version_data.get("clientVersionUpload")

        if not version_hash:
            raise DownloadError("Could not determine Roblox version from any available source.", operation="get_roblox_settings")

        log(f"Found Windows version: {version_hash}")
        base_hash = version_hash.replace("version-", "")
        extract_roots = {
            "RobloxApp.zip": "",
            "shaders.zip": "shaders/",
            "ssl.zip": "ssl/",
            "WebView2.zip": "",
            "WebView2RuntimeInstaller.zip": "WebView2RuntimeInstaller/",
            "content-avatar.zip": "content/avatar/",
            "content-configs.zip": "content/configs/",
            "content-fonts.zip": "content/fonts/",
            "content-sky.zip": "content/sky/",
            "content-sounds.zip": "content/sounds/",
            "content-textures2.zip": "content/textures/",
            "content-models.zip": "content/models/",
            "content-platform-fonts.zip": "PlatformContent/pc/fonts/",
            "content-platform-dictionaries.zip": "PlatformContent/pc/shared_compression_dictionaries/",
            "content-terrain.zip": "PlatformContent/pc/terrain/",
            "content-textures3.zip": "PlatformContent/pc/textures/",
            "extracontent-luapackages.zip": "ExtraContent/LuaPackages/",
            "extracontent-translations.zip": "ExtraContent/translations/",
            "extracontent-models.zip": "ExtraContent/models/",
            "extracontent-textures.zip": "ExtraContent/textures/",
            "extracontent-places.zip": "ExtraContent/places/",
        }
        log(f"Downloading {len(extract_roots)} required packages...")

        target_dir = os.path.expandvars(
            r"%LOCALAPPDATA%\Roblox\Versions\\" + version_hash
        )
        os.makedirs(target_dir, exist_ok=True)
        temp_dir = os.path.expandvars(r"%temp%\slate")
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
        os.makedirs(temp_dir, exist_ok=True)
        success_count = 0
        failed_packages = []

        with tqdm(
            total=len(extract_roots),
            desc="Downloading Roblox packages",
            unit="pkg",
            file=sys.stdout,
            dynamic_ncols=True,
        ) as pbar:
            for package_index, package in enumerate(extract_roots.keys()):
                package_url = f"https://setup.roblox.com/version-{base_hash}-{package}"
                pbar.set_description(f"Downloading {package}")
                try:
                    headers = {"User-Agent": "WEAO-3PService/1.0"}
                    response = requests.get(
                        package_url, stream=True, headers=headers, verify=False
                    )
                    response.raise_for_status()
                    unique_id = str(uuid.uuid4())[:8]
                    temp_file = os.path.join(temp_dir, f"{unique_id}_{package}")
                    total_size = int(response.headers.get("content-length", 0))
                    with open(temp_file, "wb") as f:

                        file_pbar = CustomProgressBar(
                            total_size,
                            f"  {package}",
                            package_index,
                            len(extract_roots),
                            config,
                        )
                        try:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    file_pbar.update(len(chunk))
                        finally:
                            file_pbar.close()

                    try:
                        with zipfile.ZipFile(temp_file, "r") as zip_ref:
                            extract_root = extract_roots[package]
                            for member in zip_ref.namelist():
                                if member.endswith("/") or member.endswith("\\"):
                                    continue
                                clean_member = member.replace("\\", "/")
                                if extract_root:
                                    target_path = os.path.join(
                                        target_dir, extract_root + clean_member
                                    )
                                else:
                                    target_path = os.path.join(target_dir, clean_member)
                                parent_dir = os.path.dirname(target_path)
                                if parent_dir:
                                    os.makedirs(parent_dir, exist_ok=True)
                                with zip_ref.open(member) as source:
                                    with open(target_path, "wb") as target_file:
                                        target_file.write(source.read())
                        log(f"  ✅ {package} downloaded and extracted")
                        success_count += 1
                    except zipfile.BadZipFile as e:
                        raise DownloadError(
                            f"Downloaded package {package} is corrupted or not a valid zip file",
                            operation="extract_package",
                            details={"package": package, "error": str(e)},
                        )
                        log(f"ZIP extraction error: {e}")
                    try:
                        os.remove(temp_file)
                    except OSError as e:
                        log(f"  ⚠️  Could not remove temporary file {temp_file}: {e}")
                except requests.RequestException as e:
                    error_msg = f"Failed to download {package}: {e}"
                    log(f"  ❌ {error_msg}")
                    failed_packages.append(package)
                    raise DownloadError(
                        error_msg,
                        operation="download_package",
                        details={"package": package, "url": package_url},
                    )
                except Exception as e:
                    error_msg = f"Unexpected error downloading {package}: {e}"
                    log(f"  ❌ {error_msg}")
                    failed_packages.append(package)
                    raise DownloadError(
                        error_msg,
                        operation="download_package",
                        details={"package": package, "error": str(e)},
                    )
                finally:
                    pbar.update(1)
        log(f"✅ Successfully downloaded {success_count}/{len(extract_roots)} packages")
        app_settings_content = """<?xml version="1.0" encoding="UTF-8"?>
<Settings>
    <ContentFolder>content</ContentFolder>
    <BaseUrl>http://www.roblox.com</BaseUrl>
</Settings>"""
        app_settings_path = os.path.join(target_dir, "AppSettings.xml")
        try:
            with open(app_settings_path, "w", encoding="utf-8") as f:
                f.write(app_settings_content)
            log(f"  ✅ Created AppSettings.xml")
        except Exception as e:
            log(f"  ❌ Failed to create AppSettings.xml: {e}")
        if success_count < len(extract_roots):
            if failed_packages:
                log(
                    f"⚠️  Some packages failed to download: {', '.join(failed_packages)}"
                )
            else:
                log(
                    f"⚠️  Some packages failed to download, but {success_count} succeeded"
                )
        if success_count == 0:
            raise DownloadError(
                "No packages were successfully downloaded",
                operation="download_all_packages",
                details={
                    "total_packages": len(extract_roots),
                    "failed_packages": failed_packages,
                },
            )
        return f"https://setup.roblox.com/version-{base_hash}"
    except DownloadError:
        raise
    except requests.RequestException as e:
        raise NetworkError(
            f"Network error while fetching Roblox version info: {e}",
            operation="fetch_version_info",
            details={"url": version_url},
        )
    except Exception as e:
        raise DownloadError(
            f"Unexpected error in get_roblox_client_settings: {e}",
            operation="get_roblox_client_settings",
            details={"error": str(e)},
        )
        log(f"Network error in get_roblox_settings: {e}")


def check_for_updates():
    log("Checking for updates...")
    try:
        response = requests.get(VERSION_URL, timeout=5)
        if response.status_code == 200:
            remote_version = response.text.strip()
            if remote_version != VERSION:
                print(f"\n[!] New version available: {remote_version} (Current: {VERSION})")
                print(f"Please download the latest version from: {download_url}")
                try:
                    pyperclip.copy(download_url)
                    print("(Link copied to clipboard)")
                except Exception:
                    pass
                print("\n")
                time.sleep(2)
    except Exception as e:
        log(f"Update check failed: {e}")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    global LOG

    slate_settings = load_slate_settings()
    if not slate_settings.get("show_console", True):
        hide_console()

    if not is_admin():
        print("Administrator privileges required. Attempting to relaunch...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)

    log("Starting Slate main function")
    config = load_cfg()

    if not validate_cfg(config):
        print("❌ Invalid configuration. Please fix the issues in slate.config.json")
        raise ConfigurationError(
            "Configuration validation failed",
            operation="validate_config",
            details={"config": config},
        )

    BANNER = r"""
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐     ▄████████  ▄█          ▄████████     ███        ▄████████   ▌
▐    ███    ███ ███         ███    ███ ▀█████████▄   ███    ███   ▌
▐    ███    █▀  ███         ███    ███    ▀███▀▀██   ███    █▀    ▌
▐    ███        ███         ███    ███     ███   ▀  ▄███▄▄▄       ▌
▐  ▀███████████ ███       ▀███████████     ███     ▀▀███▀▀▀       ▌
▐           ███ ███         ███    ███     ███       ███    █▄    ▌
▐     ▄█    ███ ███▌    ▄   ███    ███     ███       ███    ███   ▌
▐   ▄████████▀  █████▄▄██   ███    █▀     ▄████▀     ██████████   ▌
▐               ▀                                                 ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
 by: midinterlude (logs can be found in the misc folder)
 """

    def title(cfg=None, debug_mode=False):
        if (
            cfg
            and cfg.get("general", {}).get("clear_screen_on_sections", False)
            and not debug_mode
        ):
            os.system("cls")
        print(BANNER)

    title(config)
    print(f"Slate v{VERSION} - Roblox Fingerprint Scrubber")
    
    check_for_updates()

    LOG = config["general"]["log_enabled"]
    OPEN_LOG = config["general"]["open_log_on_exit"]
    PROCS = config["processes"]["roblox_processes"]
    PATHS = config["paths"]["temp_folders"] + config["paths"]["roblox_folders"]
    REGS = config["registry"]["roblox_keys"]

    if LOG:
        try:
            with open(LP, "w") as f:
                f.write("=== Slate Log ===\n")
                f.write(
                    "If you experience any errors, please DM 'midinterlude' on Discord.\n"
                )
                f.write(f"Configuration loaded from slate.config.json\n")
                f.write(f"Profile: {config.get('profile', 'custom')}\n")
        except Exception:
            pass

    print("\n" + "=" * 60)
    print("SLATE - CONFIGURATION SUMMARY")
    print("=" * 60)
    print(f"Configuration file: slate.config.json")
    print(f"Profile: {config.get('profile', 'custom')}")
    print(f"Log file: {LP}")
    
    for section, settings in config.items():
        if section in ["paths", "processes", "registry"]:
            continue

        print(f"\n{section.replace('_', ' ').title()} Options:")
        if isinstance(settings, dict):
            for key, value in settings.items():
                if isinstance(value, bool):
                    status = "[+]" if value else "[-]"
                    display_key = key.replace('_', ' ').title()
                    print(f"  {status} {display_key}")
        else:
            print(f"  - Section '{section}' has a non-standard format.")

    print("=" * 60)
    print("\nStarting in 5 seconds...")
    time.sleep(5)
    errors = []
    operation_start_time = {}

    def log_op_start(operation_name):

        operation_start_time[operation_name] = time.time()
        log(f"Starting {operation_name}...")

    def log_op_end(operation_name, success=True, error_msg=None):

        if operation_name in operation_start_time:
            duration = time.time() - operation_start_time[operation_name]
            if success:
                log(f"{operation_name} completed in {duration:.2f}s")
            else:
                log(f"{operation_name} failed after {duration:.2f}s: {error_msg}")

    try:
        if config["cleaning"]["kill_processes"]:
            log_op_start("Process termination")
            for process in PROCS:
                result = run_cmd(["taskkill", "/f", "/im", process])
                if result and result.returncode == 0:
                    log(f"  Terminated: {process}")
                else:
                    log(f"  - {process} not running or already terminated")
            log_op_end("Process termination")
        if config["cleaning"]["clean_folders"]:
            log_op_start("Folder cleaning")
            try:
                clean_folders(PATHS)
                log_op_end("Folder cleaning")
            except FileOperationError as e:
                log_op_end("Folder cleaning", False, str(e))
                errors.append(f"Folder cleaning failed: {e}")
                log(f"Detailed error info: {e.details}")
        if config["cleaning"]["remove_cookies"]:
            log_op_start("Cookie removal")
            try:
                remove_cookies()
                log_op_end("Cookie removal")
            except FileOperationError as e:
                log_op_end("Cookie removal", False, str(e))
                errors.append(f"Cookie removal failed: {e}")
        if config["cleaning"].get("clean_browser_cookies", False):
            log_op_start("Browser cookie cleaning")
            try:
                clean_browser_cookies()
                log_op_end("Browser cookie cleaning")
            except Exception as e:
                log_op_end("Browser cookie cleaning", False, str(e))
                errors.append(f"Browser cookie cleaning failed: {e}")
        if config["cleaning"]["flush_dns"]:
            log_op_start("DNS cache flush")
            result = run_cmd(["ipconfig", "/flushdns"])
            if result and result.returncode == 0:
                log_op_end("DNS cache flush")
            else:
                log_op_end("DNS cache flush", False, "Command failed")
                log("  Error flushing DNS cache")
                errors.append("DNS flush failed")
        if config["general"]["clear_screen_on_sections"]:
            title(config)
        if config["cleaning"]["restart_explorer"]:
            log_op_start("Explorer restart")
            try:
                run_cmd(["taskkill", "/f", "/im", "explorer.exe"])
                log("  Explorer terminated")
                run_cmd(["explorer.exe"])
                log("  Explorer restarted")
                log_op_end("Explorer restart")
                title(config)
            except ProcessError as e:
                log_op_end("Explorer restart", False, str(e))
                errors.append(f"Explorer restart failed: {e}")
        if config["cleaning"]["clean_registry"]:
            log_op_start("Registry cleanup")
            registry_errors = []
            for path in REGS:
                result = run_cmd(["reg", "delete", path, "/f"])
                if result and result.returncode == 0:
                    log(f"  Deleted registry: {path}")
                else:
                    log(f"  - Registry path not found or already deleted: {path}")
                    registry_errors.append(path)
            if registry_errors:
                log_op_end(
                    "Registry cleanup",
                    False,
                    f"Some registry paths not found: {registry_errors}",
                )
            else:
                log_op_end("Registry cleanup")
            title(config)
        if config["cleaning"]["clean_prefetch"]:
            log_op_start("Prefetch cleanup")
            prefetch_files = glob.glob(PF)
            if prefetch_files:
                prefetch_errors = []
                for file in prefetch_files:
                    try:
                        os.remove(file)
                        log(f"  Removed prefetch: {os.path.basename(file)}")
                    except Exception as e:
                        error_msg = f"Error removing prefetch file {file}: {e}"
                        prefetch_errors.append(error_msg)
                        log(f"  {error_msg}")
                if prefetch_errors:
                    log_op_end(
                        "Prefetch cleanup",
                        False,
                        f"Failed to remove {len(prefetch_errors)} files",
                    )
                else:
                    log_op_end("Prefetch cleanup")
            else:
                log("  - No prefetch files found")
                log_op_end("Prefetch cleanup")
            title(config)

        if config["tools"]["SpoofMAC"]:
            log_op_start("SpoofMAC")
            try:
                SpoofMAC(config, wait=True)
                log_op_end("SpoofMAC")
                log("  Waiting for network to stabilize...")
                if wait_for_connection():
                    log("  Network connection established.")
                else:
                    log("  ⚠️  Network connection check timed out.")
            except (NetworkError, ProcessError) as e:
                log_op_end("SpoofMAC", False, str(e))
                errors.append(f"SpoofMAC failed: {e}")
                log(f"Detailed SpoofMAC error info: {e.details}")

        if config["roblox"]["download_roblox"]:
            log_op_start("Roblox client download")
            try:
                get_roblox_settings(config)
                log_op_end("Roblox client download")
            except DownloadError as e:
                log_op_end("Roblox client download", False, str(e))
                errors.append(f"Roblox download failed: {e}")
                log(f"Detailed download error info: {e.details}")
            except Exception as e:
                log_op_end("Roblox client download", False, str(e))
                errors.append(f"Roblox download failed with unexpected error: {e}")
        log("\nCleaning complete!")

        if errors:
            log("\nSome operations reported issues:")
            for i, e in enumerate(errors, 1):
                log(f"   {i}. {e}")

        show_completion_popup()

        if config["advanced"]["auto_restart_after_cleaning"]:
            if OPEN_LOG and LOG:
                log_thread = threading.Thread(target=open_log, daemon=True)
                log_thread.start()
            run_cmd("shutdown /r /t 0", capture_output=False, shell=True)
        else:
            if config["roblox"]["launch_roblox_on_exit"]:
                title(config)
                log_op_start("Roblox launch")
                if launch_roblox():
                    log_op_end("Roblox launch")
                    log("Roblox is starting up!")
                else:
                    log_op_end("Roblox launch", False, "Launch failed")
                    log("Failed to launch Roblox automatically")
                    log(
                        "   You can launch it manually from the Roblox Player shortcut"
                    )
            log(
                "\nExiting without restarting. (You may want to restart manually to ensure all changes take effect.)"
            )
            print(
                "Thank you for using Slate! If you had any issues, please DM 'midinterlude' on Discord with log file."
            )

            if LOG:
                pass
            if not config["advanced"]["skip_confirmation_prompts"]:
                auto_close()
            if OPEN_LOG and LOG:
                log_thread = threading.Thread(target=open_log, daemon=True)
                log_thread.start()

            os._exit(0)
    except KeyboardInterrupt:
        log("\nOperation cancelled by user")
        print("\nOperation cancelled by user.")
        auto_close()
        os._exit(1)
    except SlateError as e:
        log(f"\nSlate error in {e.operation}: {e}")
        log(f"Detailed error info: {e.details}")
        print(f"\nError in {e.operation}: {e}")
        if config["general"]["log_enabled"]:
            print(f"Check log file for details: {LP}")
    except Exception as e:
        log(f"\nUnexpected error: {e}")

        log(f"Full traceback: {traceback.format_exc()}")
        print(f"\nUnexpected error: {e}")
        if config["general"]["log_enabled"]:
            print(f"Check log file for details: {LP}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Failed to start application: {e}")
        input("Press Enter to exit...")
        exit(1)
