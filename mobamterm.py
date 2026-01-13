import os, sys, zipfile, shutil

# UI Colors (ANSI escape codes)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

if os.name == 'nt':
    os.system('color') # Enable ANSI support on Windows

VariantBase64Table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
VariantBase64Dict = { i : VariantBase64Table[i] for i in range(len(VariantBase64Table)) }
VariantBase64ReverseDict = { VariantBase64Table[i] : i for i in range(len(VariantBase64Table)) }

def VariantBase64Encode(bs : bytes):
    result = b''
    blocks_count, left_bytes = divmod(len(bs), 3)

    for i in range(blocks_count):
        coding_int = int.from_bytes(bs[3 * i:3 * i + 3], 'little')
        block = VariantBase64Dict[coding_int & 0x3f]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3f]
        block += VariantBase64Dict[(coding_int >> 12) & 0x3f]
        block += VariantBase64Dict[(coding_int >> 18) & 0x3f]
        result += block.encode()

    if left_bytes == 0:
        return result
    elif left_bytes == 1:
        coding_int = int.from_bytes(bs[3 * blocks_count:], 'little')
        block = VariantBase64Dict[coding_int & 0x3f]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3f]
        result += block.encode()
        return result
    else:
        coding_int = int.from_bytes(bs[3 * blocks_count:], 'little')
        block = VariantBase64Dict[coding_int & 0x3f]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3f]
        block += VariantBase64Dict[(coding_int >> 12) & 0x3f]
        result += block.encode()
        return result

def EncryptBytes(key : int, bs : bytes):
    result = bytearray()
    for i in range(len(bs)):
        result.append(bs[i] ^ ((key >> 8) & 0xff))
        key = result[-1] & key | 0x482D
    return bytes(result)

class LicenseType:
    Professional = 1
    Educational = 3
    Persional = 4

def GenerateLicense(Type : LicenseType, Count : int, UserName : str, MajorVersion : int, MinorVersion : int):
    assert(Count >= 0)
    LicenseString = '%d#%s|%d%d#%d#%d3%d6%d#%d#%d#%d#' % (Type, 
                                                          UserName, MajorVersion, MinorVersion, 
                                                          Count, 
                                                          MajorVersion, MinorVersion, MinorVersion,
                                                          0,    # Unknown
                                                          0,    # No Games flag
                                                          0)    # No Plugins flag
    EncodedLicenseString = VariantBase64Encode(EncryptBytes(0x787, LicenseString.encode())).decode()
    with zipfile.ZipFile('Custom.mxtpro', 'w') as f:
        f.writestr('Pro.key', data = EncodedLicenseString)

def find_mobaxterm_install():
    # Priority 1: Default Path
    default_path = r"C:\Program Files (x86)\Mobatek\MobaXterm"
    if os.path.exists(os.path.join(default_path, "MobaXterm.exe")):
        return default_path
    
    # Priority 2: Other common paths
    common_paths = [
        r"C:\Program Files\Mobatek\MobaXterm",
        os.path.expandvars(r"%LOCALAPPDATA%\Mobatek\MobaXterm")
    ]
    for p in common_paths:
        if os.path.exists(os.path.join(p, "MobaXterm.exe")):
            return p
            
    # Priority 3: Search in Program Files (Recursive)
    print(f"{Colors.WARNING}[*] MobaXterm not found in default locations. Searching...{Colors.ENDC}")
    search_roots = [
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    ]
    for root in search_roots:
        if not os.path.exists(root): continue
        for dirpath, dirnames, filenames in os.walk(root):
            if "MobaXterm.exe" in filenames:
                return dirpath
    
    return None

def get_version_from_file(install_dir):
    v_file = os.path.join(install_dir, "version.dat")
    if os.path.exists(v_file):
        try:
            with open(v_file, 'r') as f:
                line = f.readline().strip()
                if line and '.' in line:
                    return line
        except:
            pass
    return None

def banner():
    print(f"{Colors.CYAN}")
    print("  __  __       _          __  __ _                      ")
    print(" |  \\/  |     | |        |  \\/  | |                     ")
    print(" | \\  / | ___ | |__   __ | \\  / | |_ ___ _ __ _ __ ___  ")
    print(" | |\\/| |/ _ \\| '_ \\ / _`| |\\/| | __/ _ \\ '__| '_ ` _ \\ ")
    print(" | |  | | (_) | |_) | (_| | |  | | ||  __/ |  | | | | | |")
    print(" |_|  |_|\\___/|_.__/ \\__,_|_|  |_|\\__\\___|_|  |_| |_| |_|")
    print("                                                         ")
    print(f"      @lavie3k         ")
    print(f"{Colors.ENDC}")
    print(f"{Colors.HEADER}========================================================{Colors.ENDC}")

def main():
    banner()
    
    # 1. Username
    default_user = "lavie3k"
    user_input = input(f"{Colors.GREEN}[?] Enter Username [{Colors.BOLD}{default_user}{Colors.ENDC}{Colors.GREEN}]: {Colors.ENDC}")
    username = user_input.strip() if user_input.strip() else default_user
    
    # 2. Find Installation
    print(f"{Colors.BLUE}[*] Detecting MobaXterm installation...{Colors.ENDC}")
    install_dir = find_mobaxterm_install()
    
    if install_dir:
        print(f"{Colors.GREEN}[+] Found MobaXterm at: {install_dir}{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}[-] Could not find MobaXterm installation directory.{Colors.ENDC}")
        # Ask user for manual path?
        manual_path = input(f"{Colors.WARNING}[?] Enter path manually: {Colors.ENDC}").strip()
        if manual_path and os.path.exists(manual_path):
            install_dir = manual_path
        else:
            print(f"{Colors.FAIL}[!] Cannot proceed without valid path.{Colors.ENDC}")
            input("Press Enter to exit...")
            return

    # 3. Detect Version
    version = get_version_from_file(install_dir)
    if version:
        print(f"{Colors.GREEN}[+] Detected Version: {version}{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}[!] Could not detect version from 'version.dat'.{Colors.ENDC}")
        version_input = input(f"{Colors.WARNING}[?] Enter Version manually (e.g. 25.2): {Colors.ENDC}").strip()
        if version_input:
            version = version_input
        else:
            print(f"{Colors.FAIL}[!] Version is required.{Colors.ENDC}")
            return
            
    # Parse version
    try:
        parts = version.split('.')
        major = int(parts[0])
        minor = int(parts[1])
    except:
        print(f"{Colors.FAIL}[!] Invalid version format. Must be Major.Minor (e.g. 25.2){Colors.ENDC}")
        return

    # 4. Generate
    print(f"{Colors.BLUE}[*] Generating license...{Colors.ENDC}")
    try:
        GenerateLicense(LicenseType.Professional, 1, username, major, minor)
        print(f"{Colors.GREEN}[+] 'Custom.mxtpro' generated successfully!{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}[!] Error generating license: {e}{Colors.ENDC}")
        return

    # 5. Copy
    dest_file = os.path.join(install_dir, "Custom.mxtpro")
    print(f"{Colors.BLUE}[*] Copying to installation directory...{Colors.ENDC}")
    try:
        shutil.copy("Custom.mxtpro", dest_file)
        print(f"{Colors.GREEN}[+] Successfully copied to: {dest_file}{Colors.ENDC}")
        print(f"{Colors.HEADER}========================================================{Colors.ENDC}")
        print(f"{Colors.GREEN}All done! Open MobaXterm to verify.{Colors.ENDC}")
    except PermissionError:
        print(f"{Colors.FAIL}[!] Permission denied. Try running as Administrator.{Colors.ENDC}")
        print(f"{Colors.WARNING}[*] You can manually copy 'Custom.mxtpro' to '{install_dir}'{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}[!] Error copying file: {e}{Colors.ENDC}")
    
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()
