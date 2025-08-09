#!/usr/bin/env python3
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
        import matplotlib.pyplot as plt
    except ImportError:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography", "requests", "matplotlib"])
        
        # Try importing again after installation
        try:
            import tkinter
            from cryptography.fernet import Fernet
            import requests
            import matplotlib.pyplot as plt
        except ImportError as e:
            print(f"Error: Failed to import required packages: {e}")
            print("Please install the missing packages manually:")
            print("pip install cryptography requests matplotlib")
            input("Press Enter to exit...")
            sys.exit(1)
    
    # Launch the wallet GUI
    from aleo_wallet_gui import main as run_gui
    run_gui()

if __name__ == "__main__":
    main()
