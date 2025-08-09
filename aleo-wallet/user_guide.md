# Aleo Wallet User Guide

## Introduction
Welcome to the enhanced Aleo Wallet! This guide provides comprehensive information about the wallet's features, including the newly added Web3 functionality, improved data persistence, and enhanced visual design.

## New Features and Improvements

### 1. Fixed Data Persistence
- Wallet data is now properly saved when the application closes
- Automatic saving every 5 minutes to prevent data loss
- Transaction data is immediately saved after any account modifications
- Improved error handling for file operations

### 2. Web3 Integration
- Connect to Aleo blockchain through RPC endpoints
- Interact with decentralized applications (dApps)
- View network information including latest block height
- Manage dApp connections and permissions

### 3. Enhanced Visual Design
- Improved color scheme with lighter blue (#3B82F6)
- Better contrast with black text on light grey backgrounds
- Enhanced logo visibility
- More readable interface elements

### 4. Attribution
- Created by Magnafic0 Unchained
- Powered by Giskard Reventlov (from Isaac Asimov's Robot series)

## Getting Started

### Installation
1. Extract all files from the zip archive
2. Ensure you have Python 3.8 or higher installed
3. Install required dependencies:
   ```
   pip install tkinter matplotlib requests cryptography pillow
   ```
4. Run the wallet:
   ```
   python aleo_wallet_gui_fixed.py
   ```

### Creating or Importing an Account
1. Launch the wallet application
2. Click "Create New Account" or "Import Account"
3. Follow the on-screen instructions
4. Your account will be automatically saved

## Using the Wallet

### Dashboard
- View your account balance and recent transactions
- Send and receive Aleo tokens
- Monitor real-time Aleo price

### Transactions
- View your transaction history
- Filter transactions by type or date
- Export transaction data

### Settings
- Customize wallet appearance
- Configure network settings
- Manage security preferences

### Web3 Tab
- Connect to Aleo RPC endpoints
- View blockchain information
- Manage dApp connections
- Monitor Web3 connection status

## Web3 Features

### Connecting to the Aleo Network
1. Navigate to the Web3 tab
2. Enter an RPC endpoint URL (default: https://api.aleo.network/v1)
3. Click "Connect"
4. The connection status will update to "Connected" if successful

### Viewing Network Information
- Latest block height is displayed in the Network Information section
- Click "Update" to refresh the information

### Managing dApp Connections
- Connected dApps are listed in the Connected dApps section
- You can view connection details including permissions
- Select a dApp and click "Disconnect Selected" to revoke access

### Interacting with dApps
- dApps can request connection to your wallet
- You'll be prompted to approve or deny connection requests
- You can approve or deny transaction signing requests
- All interactions are secured and require your explicit permission

## Security Recommendations
- Keep your private keys secure and never share them
- Verify transaction details before signing
- Regularly back up your wallet data
- Only connect to trusted dApps
- Use strong passwords for wallet encryption

## Troubleshooting

### Wallet Data Not Saving
- Ensure you have write permissions to the wallet directory
- Check that no other process is locking the data file
- Try running the wallet as administrator

### Connection Issues
- Verify your internet connection
- Try a different RPC endpoint
- Check if the Aleo network is experiencing issues

### dApp Connection Problems
- Ensure the dApp is compatible with the Aleo wallet
- Try refreshing the dApp page
- Clear browser cache if using a browser-based dApp

## Support
If you encounter any issues or have questions, please refer to the testing instructions document or contact support.

Thank you for using the Aleo Wallet!
