# Aleo Wallet Testing Instructions

## Overview
This document provides instructions for testing the updated Aleo wallet with fixed data persistence and new Web3 functionality. Since the wallet uses GUI components that require a desktop environment, these tests should be performed on your local machine.

## Prerequisites
Before testing, ensure you have the following installed:
- Python 3.8 or higher
- Required Python packages:
  ```
  pip install tkinter matplotlib requests cryptography pillow
  ```

## Testing Data Persistence Fix

### Test 1: Wallet Data Saving on Exit
1. Launch the wallet application:
   ```
   python aleo_wallet_gui_fixed.py
   ```
2. Create a new account or import an existing one
3. Make changes to settings or account data
4. Close the wallet application
5. Reopen the wallet
6. **Expected Result**: All your account data and settings should be preserved

### Test 2: Wallet Data Saving After Transactions
1. Launch the wallet application
2. Send a test transaction (can be to your own address)
3. Close the wallet immediately after the transaction
4. Reopen the wallet
5. **Expected Result**: The transaction should appear in your history and your balance should be updated

### Test 3: Auto-Save Functionality
1. Launch the wallet application
2. Make changes to your account or settings
3. Wait for 5 minutes without closing the wallet
4. Force-close the application (using Task Manager or equivalent)
5. Reopen the wallet
6. **Expected Result**: Changes made before the force-close should be preserved

## Testing Web3 Functionality

### Test 1: RPC Connection
1. Launch the wallet application
2. Navigate to the Web3 tab
3. Enter a valid Aleo RPC endpoint (e.g., "https://api.aleo.network/v1")
4. Click "Connect"
5. **Expected Result**: Status should change to "Connected" and network information should be displayed

### Test 2: Network Information
1. While on the Web3 tab with an active connection
2. Click the "Update" button
3. **Expected Result**: Latest block height should be displayed

### Test 3: dApp Connection Simulation
Since actual dApp connections require browser integration, we can simulate this:
1. Launch the wallet application
2. Open a Python console in another window
3. Run the following code to simulate a dApp connection:
   ```python
   import requests
   import json
   
   # Replace with your wallet's local server address if different
   wallet_url = "http://localhost:8000/web3"
   
   # Simulate a connection request
   connection_request = {
       "method": "connect",
       "params": {
           "dapp_url": "https://test-dapp.com",
           "dapp_name": "Test dApp",
           "requested_permissions": ["view_accounts", "sign_transactions"]
       }
   }
   
   response = requests.post(
       wallet_url,
       headers={"Content-Type": "application/json"},
       data=json.dumps(connection_request)
   )
   
   print(response.json())
   ```
4. In the wallet, navigate to the Web3 tab
5. Click "Refresh List"
6. **Expected Result**: The test dApp should appear in the connected dApps list

## Testing Color Contrast and Logo Visibility

### Test 1: Text Readability
1. Launch the wallet application
2. Navigate through different tabs and sections
3. **Expected Result**: All text should be clearly readable with black text on light grey backgrounds

### Test 2: Logo Visibility
1. Launch the wallet application
2. Look at the logo in the header area
3. **Expected Result**: The logo should be clearly visible and properly sized

## Reporting Issues
If you encounter any issues during testing, please provide the following information:
1. Test case that failed
2. Expected vs. actual behavior
3. Screenshots if applicable
4. Any error messages displayed
5. Your operating system and Python version
