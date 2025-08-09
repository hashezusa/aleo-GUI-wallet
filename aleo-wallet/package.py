import os
import sys
import shutil
import zipfile
import tempfile
import subprocess
from pathlib import Path

def package_wallet():
    """
    Package the Aleo wallet for distribution.
    Creates a zip file containing all necessary files.
    """
    print("Packaging Aleo Wallet for distribution...")
    
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, "dist")
    
    # Ensure dist directory exists
    os.makedirs(dist_dir, exist_ok=True)
    
    # Define the files to include
    files_to_include = [
        "aleo_api.py",
        "wallet_core.py",
        "transaction_manager.py",
        "address_book.py",
        "security.py",
        "blockchain_integration.py",
        "aleo_wallet_gui.py",
        "README.md",
    ]
    
    # Create a temporary directory for building the package
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy files to the temporary directory
        for file in files_to_include:
            src_path = os.path.join(base_dir, file)
            if os.path.exists(src_path):
                shutil.copy2(src_path, temp_dir)
            else:
                print(f"Warning: File {file} not found, skipping...")
        
        # Create the main executable script
        with open(os.path.join(temp_dir, "aleo_wallet.py"), "w") as f:
            f.write("""#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    
    # Check for required packages
    try:
        import tkinter
        from cryptography.fernet import Fernet
        import requests
    except ImportError:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography", "requests"])
    
    # Launch the wallet GUI
    from aleo_wallet_gui import main as run_gui
    run_gui()

if __name__ == "__main__":
    main()
""")
        
        # Make the script executable
        os.chmod(os.path.join(temp_dir, "aleo_wallet.py"), 0o755)
        
        # Create a Windows batch file
        with open(os.path.join(temp_dir, "aleo_wallet.bat"), "w") as f:
            f.write("""@echo off
python aleo_wallet.py
pause
""")
        
        # Create a zip file
        zip_path = os.path.join(dist_dir, "aleo_wallet.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
    
    print(f"Package created: {zip_path}")
    
    # Create a standalone executable using PyInstaller if available
    try:
        import PyInstaller
        print("Creating standalone executable with PyInstaller...")
        
        # Create a spec file
        spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['aleo_wallet.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='aleo_wallet',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
"""
        
        with open(os.path.join(base_dir, "aleo_wallet.spec"), "w") as f:
            f.write(spec_content)
        
        # Run PyInstaller
        subprocess.run([
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name", "aleo_wallet",
            os.path.join(base_dir, "aleo_wallet.py")
        ], check=True)
        
        # Copy the executable to the dist directory
        exe_path = os.path.join(base_dir, "dist", "aleo_wallet")
        if os.path.exists(exe_path):
            shutil.copy2(exe_path, dist_dir)
            print(f"Standalone executable created: {os.path.join(dist_dir, 'aleo_wallet')}")
        
        # Clean up PyInstaller files
        for path in ["build", "dist", "aleo_wallet.spec"]:
            path = os.path.join(base_dir, path)
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.exists(path):
                os.remove(path)
    
    except (ImportError, subprocess.SubprocessError) as e:
        print(f"Could not create standalone executable: {e}")
        print("The wallet can still be used from the zip package.")
    
    return zip_path

if __name__ == "__main__":
    package_wallet()
