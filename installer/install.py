import requests
import zipfile
import pathlib
import os
import platform


def get_appdata():
    return pathlib.Path.home() / "AppData" / "Roaming"


def remove_dir(path: pathlib.Path):
    if path.exists():
        for file in path.glob("*"):
            if file.is_file():
                file.unlink()
            else:
                remove_dir(file)
        path.rmdir()


def ensure_dir(path: pathlib.Path, cleanup=False):
    if cleanup:
        remove_dir(path)
    if not path.exists():
        path.mkdir()


def ensure_no_dir(path: pathlib.Path):
    if path.exists():
        try:
            path.rmdir()
        except OSError:
            print(f"{path} is not empty.")
            do = input("Do you want to delete it? (y/n) ")
            if do.lower() == "y":
                remove_dir(path)
            else:
                print("Aborting.")
                exit(1)


def download_file(url, filename):
    with open(filename, "wb") as f:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        for block in response.iter_content(1024):
            f.write(block)


##########

print()
print("----------")
print()

arch = platform.machine().lower()

if not arch in ("amd64", "win32", "arm64"):
    print("Unsupported architecture:", arch)
    print("Please contact the developer for support.")
    exit(1)

is_update = False

RULES_BACKUP = get_appdata() / "StudioCustomNames_rules_backup"
INSTALL_DIR = get_appdata() / "StudioCustomNames"
ZIP_FILE = get_appdata() / "StudioCustomNames.zip"
EXTRACT_DIR = get_appdata() / "studio-custom-names-main"

if os.path.exists(get_appdata() / "StudioCustomNames" / "rules"):
    print("Found existing installation.")
    do = input("Do you want to reinstall/upgrade? Rules will be backed up. (y/n) ")
    if do.lower() == "y":
        ensure_dir(RULES_BACKUP, cleanup=True)
        os.rename(INSTALL_DIR / "rules", RULES_BACKUP / "rules")
        remove_dir(INSTALL_DIR)
        is_update = True
    else:
        print("Aborting.")
        exit(1)

ensure_no_dir(INSTALL_DIR)
ensure_no_dir(EXTRACT_DIR)

print("Downloading StudioCustomNames...")
download_file(
    "https://github.com/GSG-Robots/studio-custom-names/archive/refs/heads/main.zip",
    ZIP_FILE,
)

print("Extracting StudioCustomNames...")
with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
    zip_ref.extractall(EXTRACT_DIR.parent)

os.rename(EXTRACT_DIR, INSTALL_DIR)

print("Downloading Python...")
download_file(
    f"https://www.python.org/ftp/python/3.12.2/python-3.12.2-embed-{arch}.zip",
    INSTALL_DIR / "python-3.12.2-embed.zip",
)

print("Downloading PIP...")
download_file(
    "https://bootstrap.pypa.io/get-pip.py",
    INSTALL_DIR / "installer" / "get-pip.py",
)

print("Extracting Python...")
with zipfile.ZipFile(INSTALL_DIR / "python-3.12.2-embed.zip", "r") as zip_ref:
    zip_ref.extractall(INSTALL_DIR / "python-embed")

print("Activating PIP...")
with open(INSTALL_DIR / "python-embed" / "python312._pth", "a", encoding="utf-8") as f:
    f.write("import site\n")

print("Installing PIP...")
os.system(
    f"{INSTALL_DIR / 'python-embed' / 'python.exe'} {INSTALL_DIR / 'installer' / 'get-pip.py'}"
)

print("Installing requirements...")
os.system(
    f"{INSTALL_DIR / 'python-embed' / 'python.exe'} -m pip install -r {INSTALL_DIR / 'requirements.txt'}"
)

print("Cleaning up...")
os.remove(get_appdata() / "StudioCustomNames.zip")
os.remove(INSTALL_DIR / "python-3.12.2-embed.zip")

print("Setting up .bat starters...")
with open(INSTALL_DIR / "start.bat", "w", encoding="utf-8") as f:
    f.write(
        rf"""
@echo off
cd {INSTALL_DIR / "python-embed"}
.\python.exe {INSTALL_DIR / "main.py"}
echo ----------
pause
"""
    )

with open(INSTALL_DIR / "update.bat", "w", encoding="utf-8") as f:
    f.write(
        rf"""
@echo off
cd {INSTALL_DIR / "python-embed"}
.\python.exe {INSTALL_DIR / "installer" / "install.py"}
echo ----------
pause
"""
    )

print("Cleaning up...")
remove_dir(EXTRACT_DIR)

if is_update:
    do = input("Do you want to restore the rules? (y/n) ")
    if do.lower() == "y":
        remove_dir(INSTALL_DIR / "rules")
        os.rename(RULES_BACKUP / "rules", INSTALL_DIR / "rules")
        remove_dir(RULES_BACKUP)
        print("Rules are restored.")
    else:
        print("Rules are not restored. They are still backed up at", RULES_BACKUP)

print("\nInstallation complete!")
print(f"StudioCustomNames is installed at {INSTALL_DIR}.")
print("You can run it by executing start.bat.")

input("Press Enter to exit.")
